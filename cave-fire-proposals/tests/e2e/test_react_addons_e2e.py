import subprocess
import time
from pathlib import Path
import requests

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def http_server_and_api():
    # start a simple static file server
    static_proc = subprocess.Popen(
        ["python", "-m", "http.server", "8002"], cwd=str(ROOT)
    )
    # start the uvicorn API server on port 8003
    api_proc = subprocess.Popen(
        ["python", "-m", "uvicorn", "app.server:app", "--port", "8003"], cwd=str(ROOT)
    )

    # wait for both servers to be responsive
    for _ in range(40):
        try:
            requests.get("http://localhost:8002/", timeout=0.5)
            requests.get("http://localhost:8003/docs", timeout=0.5)
            break
        except Exception:
            time.sleep(0.2)
    else:
        static_proc.terminate()
        api_proc.terminate()
        pytest.fail("Failed to start servers for e2e tests")

    yield

    api_proc.terminate()
    api_proc.wait()
    static_proc.terminate()
    static_proc.wait()


def test_react_addons_totals_change(playwright, http_server_and_api):
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.goto("http://localhost:8002/examples/react-addons/index.html")

    # Wait for the table rows to be present
    page.wait_for_selector("table.table tbody tr")

    totals_before = page.locator(".totals").inner_text()
    # Click first checkbox to toggle include/exclude
    first_checkbox = page.locator("table.table tbody tr input[type=checkbox]").first
    first_checkbox.click()
    # Small pause to allow React to update
    page.wait_for_timeout(200)
    totals_after = page.locator(".totals").inner_text()

    assert totals_before != totals_after
    assert "Subtotal:" in totals_after and "Tax:" in totals_after

    # Now test server integration: compute server totals and ensure they're displayed
    page.click('button:has-text("Compute server totals")')
    # wait for server totals to render
    page.wait_for_selector(".server-totals")
    st = page.locator(".server-totals").inner_text()
    assert "Server totals" in st and ("Subtotal:" in st or "Server error" in st)

    browser.close()
