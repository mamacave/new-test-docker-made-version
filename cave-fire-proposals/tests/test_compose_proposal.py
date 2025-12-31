from pathlib import Path
from decimal import Decimal

from scripts.seeds.compose_proposal import compose


def test_compose_default_proposal():
    root = Path(__file__).resolve().parents[1]
    proposal_path = root / "seeds" / "default_proposal.json"
    out = compose(proposal_path)
    assert out["subtotal"] == Decimal("696.90")
    # Tax is calculated per-line and rounded to cents before summing
    assert out["tax"] == Decimal("9.35")
    assert out["total"] == Decimal("706.25")
