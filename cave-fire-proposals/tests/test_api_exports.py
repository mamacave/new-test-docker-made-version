import json
from fastapi.testclient import TestClient
from app.server import app

client = TestClient(app)


def load_sample():
    with open("seeds/default_proposal.json", "r", encoding="utf-8") as fh:
        return json.load(fh)


def test_compose_api():
    data = load_sample()
    res = client.post("/api/compose", json=data)
    assert res.status_code == 200
    body = res.json()
    assert "subtotal" in body


def test_export_html():
    data = load_sample()
    res = client.post("/api/export/html", json=data)
    assert res.status_code == 200
    assert "<html" in res.text.lower()


def test_export_docx():
    data = load_sample()
    # include computed totals to be rendered into docx
    from scripts.seeds.compose_proposal import compose_from_data

    totals = compose_from_data(data)
    # JSON can't serialize Decimal directly in this test payload; convert to floats
    data["totals"] = {k: float(v) for k, v in totals.items()}
    res = client.post("/api/export/docx", json=data)
    assert res.status_code == 200
    assert res.headers.get("content-type").startswith(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert len(res.content) > 1000
