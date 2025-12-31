from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from io import BytesIO
from typing import Any, Dict

from scripts.seeds.compose_proposal import compose_from_data, load_json
from scripts.export.docx_export import proposal_to_docx_bytes
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"

app = FastAPI(title="Cave Fire Proposals API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATES),
    autoescape=select_autoescape(["html", "xml"]),
)

# Serve static example files under /examples
from fastapi.staticfiles import StaticFiles

app.mount("/examples", StaticFiles(directory=ROOT / "examples"), name="examples")


@app.post("/api/compose")
async def api_compose(payload: Dict[str, Any]):
    try:
        totals = compose_from_data(payload)
        # convert Decimals to floats for JSON serialization
        return {k: float(v) for k, v in totals.items()}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/export/html", response_class=HTMLResponse)
async def export_html(payload: Dict[str, Any]):
    # payload should be a proposal JSON; we will render using template
    tmpl = jinja_env.get_template("proposal.html")
    totals = compose_from_data(payload)
    # convert Decimals to floats for safe template formatting
    html = tmpl.render(
        proposal=payload, totals={k: float(v) for k, v in totals.items()}
    )
    return HTMLResponse(content=html)


@app.post("/api/export/docx")
async def export_docx(payload: Dict[str, Any]):
    try:
        doc_bytes = proposal_to_docx_bytes(payload)
        bio = BytesIO(doc_bytes)
        headers = {"Content-Disposition": "attachment; filename=proposal.docx"}
        return StreamingResponse(
            bio,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers=headers,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
