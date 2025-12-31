"""Small seed loader: prints totals and demonstrates a simple import from JSON/CSV.

Usage: python3 scripts/seeds/load_add_ons.py
"""

import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JSON_PATH = ROOT / "seeds" / "add_ons.json"
CSV_PATH = ROOT / "data" / "add_ons.csv"

TAX_RATE = Decimal("0.0875")  # example AZ sales tax — adjust as needed


def load_json(path=JSON_PATH):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def calculate_line_total(unit_price, quantity, taxable):
    price = Decimal(str(unit_price)) * Decimal(quantity)
    tax = (price * TAX_RATE).quantize(Decimal("0.01")) if taxable else Decimal("0.00")
    return (price + tax).quantize(Decimal("0.01"))


if __name__ == "__main__":
    items = load_json()
    print("Loaded add-ons: ", len(items))
    total = Decimal("0.00")
    for i in items:
        qty = i.get("default_quantity", 1)
        line = calculate_line_total(i["unit_price"], qty, i.get("taxable", False))
        print(f"{i['code']}: {qty} x ${i['unit_price']} => ${line}")
        total += line
    print("Grand total (with sample defaults): $", total)
