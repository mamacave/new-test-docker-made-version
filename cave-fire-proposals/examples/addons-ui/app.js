const TABLE_BODY = document.querySelector('#addonsTable tbody');
const SUBTOTAL_EL = document.getElementById('subtotal');
const TAX_EL = document.getElementById('taxtotal');
const TOTAL_EL = document.getElementById('grandtotal');
const TAX_INPUT = document.getElementById('taxRate');
const EXPORT_BTN = document.getElementById('exportCsv');
const PROPOSAL_ID = document.getElementById('proposalId');
const PROPOSAL_DATE = document.getElementById('proposalDate');
const LOGO_INPUT = document.getElementById('logo');
const LOGO_PREVIEW = document.getElementById('logoPreview');
const SIG_CANVAS = document.getElementById('sigCanvas');
const CLEAR_SIG = document.getElementById('clearSig');
const SAVE_SIG = document.getElementById('saveSig');
let savedSignature = null;

// signature simple drawing
const ctx = SIG_CANVAS.getContext('2d');
let drawing = false;
SIG_CANVAS.addEventListener('mousedown', () => drawing = true);
SIG_CANVAS.addEventListener('mouseup', () => drawing = false);
SIG_CANVAS.addEventListener('mouseleave', () => drawing = false);
SIG_CANVAS.addEventListener('mousemove', (e) => {
  if(!drawing) return; const r = SIG_CANVAS.getBoundingClientRect();
  const x = e.clientX - r.left; const y = e.clientY - r.top; ctx.lineWidth=2; ctx.lineCap='round'; ctx.strokeStyle='#111'; ctx.lineTo(x,y); ctx.stroke(); ctx.beginPath(); ctx.moveTo(x,y);
});
CLEAR_SIG.addEventListener('click', () => { ctx.clearRect(0,0,SIG_CANVAS.width,SIG_CANVAS.height); savedSignature=null; });
SAVE_SIG.addEventListener('click', () => { savedSignature = SIG_CANVAS.toDataURL('image/png'); alert('Signature saved'); });

LOGO_INPUT.addEventListener('change', (ev) => {
  const f = ev.target.files && ev.target.files[0];
  if(!f) return;
  const r = new FileReader(); r.onload = () => { LOGO_PREVIEW.innerHTML = `<img src="${r.result}" style="max-height:80px;">`; document.logoData = r.result; }; r.readAsDataURL(f);
});

let addons = [];

function cents(n){
  // Convert dollars to integer cents (works for strings or numbers)
  return Math.round(Number(n) * 100);
}

function fmtCents(c){
  return '$' + (c/100).toFixed(2);
}

function calcLine(unitPrice, qty, taxable, taxRate){
  const priceCents = cents(unitPrice);
  const lineCents = priceCents * qty;
  const taxCents = taxable ? Math.round(lineCents * (taxRate / 100)) : 0;
  const totalCents = lineCents + taxCents;
  return {lineCents, taxCents, totalCents};
}

function render(){
  TABLE_BODY.innerHTML = '';
  const taxRate = parseFloat(TAX_INPUT.value || '0');
  let subtotalC = 0, taxC = 0;

  addons.forEach((a, idx) => {
    const include = a._include;
    const qty = a._quantity || a.default_quantity || 1;
    const {lineCents, taxCents, totalCents} = calcLine(a.unit_price, qty, a.taxable && include, taxRate);
    subtotalC += lineCents * (include ? 1 : 0);
    taxC += taxCents * (include ? 1 : 0);

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><input type="checkbox" ${include ? 'checked' : ''} data-idx="${idx}" class="include"></td>
      <td>${a.code}</td>
      <td>${a.name}</td>
      <td>${a.unit}</td>
      <td>${fmtCents(cents(a.unit_price))}</td>
      <td><input type="number" min="0" value="${qty}" data-idx="${idx}" class="qty"></td>
      <td>${a.taxable ? 'Yes' : 'No'}</td>
      <td>${fmtCents(taxCents)}</td>
      <td>${fmtCents(totalCents)}</td>
    `;
    TABLE_BODY.appendChild(tr);
  });

  SUBTOTAL_EL.textContent = fmtCents(subtotalC);
  TAX_EL.textContent = fmtCents(taxC);
  TOTAL_EL.textContent = fmtCents(subtotalC + taxC);

  // wire up actions
  document.querySelectorAll('.qty').forEach(el => {
    el.addEventListener('change', (ev) => {
      const idx = Number(ev.target.dataset.idx);
      const v = Math.max(0, Math.floor(Number(ev.target.value) || 0));
      addons[idx]._quantity = v;
      render();
    });
  });
  document.querySelectorAll('.include').forEach(el => {
    el.addEventListener('change', (ev) => {
      const idx = Number(ev.target.dataset.idx);
      addons[idx]._include = ev.target.checked;
      render();
    });
  });
}

async function load(){
  try{
    const resp = await fetch('/seeds/add_ons.json');
    if(!resp.ok) throw new Error('Failed to fetch seeds/add_ons.json: ' + resp.status);
    const data = await resp.json();
    // default: include items with default_quantity > 0
    addons = data.map(a => ({...a, _include: a.default_quantity > 0, _quantity: a.default_quantity || 1}));
    render();
  }catch(err){
    TABLE_BODY.innerHTML = `<tr><td colspan="9">Error loading add-ons: ${err.message}</td></tr>`;
  }
}

function exportCsv(){
  const taxRate = parseFloat(TAX_INPUT.value || '0');
  const rows = [];
  rows.push(['code','name','unit_price','quantity','taxable','line_tax','line_total']);
  // include proposal metadata and signature/logo if present
  if(PROPOSAL_ID.value) rows.push(['proposal_id','',PROPOSAL_ID.value]);
  if(PROPOSAL_DATE.value) rows.push(['date','',PROPOSAL_DATE.value]);
  if(document.logoData) rows.push(['logo_data_url','',document.logoData]);
  if(savedSignature) rows.push(['signature_data','',savedSignature]);
  let subtotal=0,tax=0,total=0;
  addons.forEach(a => {
    if(!a._include) return;
    const qty = a._quantity || 1;
    const {lineCents,taxCents,totalCents} = calcLine(a.unit_price, qty, a.taxable, taxRate);
    rows.push([a.code,a.name,Number(a.unit_price).toFixed(2),qty,a.taxable ? 'yes' : 'no', (taxCents/100).toFixed(2),(totalCents/100).toFixed(2)]);
    subtotal += lineCents; tax += taxCents; total += totalCents;
  });
  rows.push([]);
  rows.push(['subtotal','', (subtotal/100).toFixed(2)]);
  rows.push(['tax','', (tax/100).toFixed(2)]);
  rows.push(['total','', (total/100).toFixed(2)]);

  const csv = rows.map(r => r.map(c => typeof c === 'string' && c.includes(',') ? `"${c}"` : c).join(',')).join('\n');
  const blob = new Blob([csv], {type:'text/csv'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'proposal_addons_export.csv';
  document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
}

TAX_INPUT.addEventListener('change', render);
EXPORT_BTN.addEventListener('click', exportCsv);

load();
