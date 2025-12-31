"""Compose a proposal by resolving line item codes against `seeds/add_ons.json`.

Usage: python3 scripts/seeds/compose_proposal.py seeds/default_proposal.json
"""

import json
from decimal import Decimal
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
ADDONS_PATH = ROOT / "seeds" / "add_ons.json"

TAX_RATE = Decimal("0.0875")


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def find_addon_by_code(items, code):
    for i in items:
        if i.get("code") == code:
            return i
    return None


def compose(proposal_path):
    proposal = load_json(Path(proposal_path))
    return compose_from_data(proposal)


def compose_from_data(proposal: dict):
    """Compose totals for an in-memory proposal dict (useful for APIs)."""
    addons = load_json(ADDONS_PATH)
    subtotal = Decimal("0.00")
    tax_total = Decimal("0.00")

    # Resolve line items
    for section in proposal.get("sections", []):
        for li in section.get("line_items", []) + section.get("add_ons", []):
            code = li.get("code")
            qty = li.get("quantity", 1)
            item = find_addon_by_code(addons, code)
            if item is None:
                # unknown code — skip and warn (caller may supply inline unit_price)
                if li.get("unit_price") is not None:
                    unit_price = Decimal(str(li.get("unit_price")))
                else:
                    # skip silently
                    continue
            else:
                unit_price = Decimal(str(item["unit_price"]))
            line = (unit_price * Decimal(qty)).quantize(Decimal("0.01"))
            subtotal += line
            taxable = False
            if item is not None:
                taxable = item.get("taxable", False)
            else:
                taxable = li.get("taxable", False)
            if taxable:
                tax = (line * TAX_RATE).quantize(Decimal("0.01"))
                tax_total += tax
    total = (subtotal + tax_total).quantize(Decimal("0.01"))
    return {"subtotal": subtotal, "tax": tax_total, "total": total}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
    else:
        path = ROOT / "seeds" / "default_proposal.json"

    out = compose(path)
    print("Proposal totals:")
    print(out)
