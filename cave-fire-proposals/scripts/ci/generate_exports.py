"""Generate HTML and DOCX exports for CI verification.

Usage:
    python scripts/ci/generate_exports.py artifacts

The script writes files to the given output directory and exits with non-zero
status if any generated file is empty or missing.
"""

import sys
from pathlib import Path
import json
import logging

logging.basicConfig(level=logging.INFO)

OUT_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("artifacts")
ROOT = Path(__file__).resolve().parents[2]

# Local imports from repo
from scripts.seeds.compose_proposal import compose_from_data
from scripts.export.docx_export import proposal_to_docx_bytes
from jinja2 import Environment, FileSystemLoader, select_autoescape


def load_sample_proposal() -> dict:
    path = ROOT / "seeds" / "default_proposal.json"
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def render_html(proposal: dict) -> str:
    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )
    tmpl = env.get_template("proposal.html")
    totals = compose_from_data(proposal)
    # Attach totals for rendering convenience and pass totals as a template variable
    proposal_with_totals = dict(proposal)
    proposal_with_totals["totals"] = totals
    return tmpl.render(
        proposal=proposal_with_totals, totals={k: float(v) for k, v in totals.items()}
    )


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    proposal = load_sample_proposal()

    html = render_html(proposal)
    html_path = OUT_DIR / "proposal.html"
    html_path.write_text(html, encoding="utf-8")
    logging.info("Wrote HTML to %s (%d bytes)", html_path, html_path.stat().st_size)

    docx_bytes = proposal_to_docx_bytes(proposal)
    docx_path = OUT_DIR / "proposal.docx"
    docx_path.write_bytes(docx_bytes)
    logging.info("Wrote DOCX to %s (%d bytes)", docx_path, docx_path.stat().st_size)

    # Basic verification
    failed = False
    for p in [html_path, docx_path]:
        if not p.exists() or p.stat().st_size == 0:
            logging.error("Generated artifact missing or empty: %s", p)
            failed = True

    if failed:
        sys.exit(2)

    logging.info("All exports generated successfully.")


if __name__ == "__main__":
    main()
