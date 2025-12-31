import json
from decimal import Decimal
from pathlib import Path

from scripts.seeds.load_add_ons import calculate_line_total

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "seeds" / "add_ons.json"


def test_calculate_line_total_non_taxable():
    # Fire alarm per device — non-taxable
    total = calculate_line_total(6.0, 10, False)
    assert total == Decimal("60.00")


def test_calculate_line_total_taxable():
    # Extinguisher add-on — taxable
    total = calculate_line_total(15.95, 2, True)
    # 15.95 * 2 = 31.90 ; tax 8.75% => 2.79 -> 34.69
    assert total == Decimal("34.69")


def test_load_and_sample_totals():
    with open(JSON_PATH, "r", encoding="utf-8") as fh:
        items = json.load(fh)
    assert any(i["code"] == "F-A-ANNUAL" for i in items)
    # ensure every item has price and default quantity
    for i in items:
        assert "unit_price" in i
        assert "default_quantity" in i
