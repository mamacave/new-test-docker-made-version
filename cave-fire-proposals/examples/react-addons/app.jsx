const { useState, useEffect } = React;

function fmtCents(c){ return '$' + (c/100).toFixed(2); }
function cents(n){ return Math.round(Number(n) * 100); }
function calcLine(unitPrice, qty, taxable, taxRate){
  const p = cents(unitPrice);
  const line = p * qty;
  const tax = taxable ? Math.round(line * (taxRate/100)) : 0;
  return {line, tax, total: line+tax};
}

function AddonRow({a, idx, onChange}){
  return (
    React.createElement('tr', null,
      React.createElement('td', null, React.createElement('input',{type:'checkbox', checked:a._include, onChange:e => onChange(idx,{_include:e.target.checked})})),
      React.createElement('td', null, a.code),
      React.createElement('td', null, a.name),
      React.createElement('td', null, a.unit),
      React.createElement('td', null, fmtCents(cents(a.unit_price))),
      React.createElement('td', null, React.createElement('input',{type:'number', min:0, value:a._quantity, onChange:e => onChange(idx,{_quantity:Math.max(0,Math.floor(Number(e.target.value)||0))})})),
      React.createElement('td', null, a.taxable ? 'Yes' : 'No')
    )
  );
}

function App(){
  const [addons,setAddons] = useState([]);
  const [taxRate,setTaxRate] = useState(8.75);

  useEffect(()=>{ fetch('/seeds/add_ons.json').then(r=>r.json()).then(data=>{
    setAddons(data.map(a=>({...a,_include: a.default_quantity>0, _quantity: a.default_quantity || 1}))); }); },[]);

  function update(idx, patch){
    setAddons(prev => { const copy = [...prev]; copy[idx] = {...copy[idx], ...patch}; return copy; });
  }

  let subtotal=0, tax=0;
  addons.forEach(a => { if(!a._include) return; const {line,tax:tx} = calcLine(a.unit_price,a._quantity||1,a.taxable,taxRate); subtotal+=line; tax+=tx; });

  function composePayload(){
    // Build a minimal proposal payload similar to seeds/default_proposal.json
    return {
      id: 'ui-prop',
      sections: [
        {
          title: 'UI Generated',
          line_items: [],
          add_ons: addons.filter(a=>a._include).map(a=>({code:a.code, quantity:a._quantity}))
        }
      ]
    };
  }

  async function computeServerTotals(){
    const payload = composePayload();
    try{
      const res = await fetch('http://localhost:8003/api/compose', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
      if(!res.ok) throw new Error('Server error');
      const data = await res.json();
      setServerTotals(data);
    }catch(err){
      setServerTotals({error: String(err)});
    }
  }

  const [serverTotals,setServerTotals] = useState(null);

  return (
    React.createElement('div', null,
      React.createElement('div',{className:'controls'},
        React.createElement('label',null,'Tax rate: ', React.createElement('input',{type:'number',step:'0.01',value:taxRate,onChange:e=>setTaxRate(Number(e.target.value||0))})),
        React.createElement('button',{onClick:computeServerTotals, style:{marginLeft:10}}, 'Compute server totals')
      ),
      React.createElement('table',{className:'table'},
        React.createElement('thead',null,React.createElement('tr',null, ['Include','Code','Name','Unit','Unit Price','Qty','Taxable'].map(h=>React.createElement('th',null,h)))),
        React.createElement('tbody',null,addons.map((a,idx)=>React.createElement(AddonRow,{a,idx,onChange:update})))
      ),
      React.createElement('div',{className:'totals'},
        React.createElement('div',null,'Subtotal: ',fmtCents(subtotal)),
        React.createElement('div',null,'Tax: ',fmtCents(tax)),
        React.createElement('div',{className:'grand'},'Total: ',fmtCents(subtotal+tax))
      ),
      React.createElement('div',{className:'server-totals'}, serverTotals ? (serverTotals.error ? React.createElement('div',null,'Server error: '+serverTotals.error) : React.createElement('div',null,'Server totals — Subtotal: '+ (serverTotals.subtotal/100).toFixed(2) + ' Tax: ' + (serverTotals.tax/100).toFixed(2) + ' Total: ' + (serverTotals.total/100).toFixed(2))) : React.createElement('div',null,'Server totals: (not computed)'))
    )
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(App));
