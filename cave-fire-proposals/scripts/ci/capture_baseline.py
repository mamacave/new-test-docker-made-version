"""Capture a baseline screenshot of the React add-ons example.

This script starts a static server and uvicorn similarly to the e2e tests,
captures a screenshot using Playwright, and writes it to the `artifacts/`
folder. It's intended to run in CI on a schedule and upload the artifacts
for maintainers to review and commit into `tests/e2e/baseline_screenshots/`.
"""

import subprocess
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts"
ARTIFACTS.mkdir(parents=True, exist_ok=True)

# start static server
static_proc = subprocess.Popen(["python", "-m", "http.server", "8002"], cwd=str(ROOT))
api_proc = subprocess.Popen(
    ["python", "-m", "uvicorn", "app.server:app", "--port", "8003"], cwd=str(ROOT)
)
try:
    for _ in range(40):
        try:
            import requests

            requests.get("http://localhost:8002/", timeout=0.5)
            requests.get("http://localhost:8003/docs", timeout=0.5)
            break
        except Exception:
            time.sleep(0.2)
    else:
        raise SystemExit("servers failed to start")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost:8002/examples/react-addons/index.html")
        page.wait_for_selector("table.table tbody tr")
        page.wait_for_timeout(200)
        out = ARTIFACTS / "baseline_react_addons.png"
        page.screenshot(path=str(out), full_page=True)
        print(f"Wrote baseline screenshot to {out}")
        browser.close()
finally:
    api_proc.terminate()
    api_proc.wait()
    static_proc.terminate()
    static_proc.wait()
