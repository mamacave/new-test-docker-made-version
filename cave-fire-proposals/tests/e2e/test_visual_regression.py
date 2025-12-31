import time
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
BASELINE_DIR = ROOT / "tests" / "e2e" / "baseline_screenshots"
ARTIFACTS = ROOT / "artifacts"


def ensure_dirs():
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)


def test_react_addons_visual(playwright, http_server_and_api):
    ensure_dirs()
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.goto("http://localhost:8002/examples/react-addons/index.html")
    page.wait_for_selector("table.table tbody tr")
    # give UI a moment to settle
    page.wait_for_timeout(200)

    current = ARTIFACTS / "react_addons_current.png"
    page.screenshot(path=str(current), full_page=True)

    baseline = BASELINE_DIR / "react_addons.png"
    if not baseline.exists():
        # Save baseline for the first run and skip test
        current.replace(baseline)
        pytest.skip(
            "Baseline did not exist; saved current as baseline. Commit baseline image to enable comparisons."
        )

    # Compare using helper script
    import subprocess

    diff_path = ARTIFACTS / "react_addons_diff.png"
    res = subprocess.run(
        [
            "python",
            "scripts/ci/compare_screenshots.py",
            str(baseline),
            str(current),
            "--threshold",
            "0.01",
            "--output",
            str(diff_path),
        ],
        capture_output=True,
        text=True,
    )
    print(res.stdout)
    print(res.stderr)
    if res.returncode != 0:
        print(f"Diff saved to {diff_path}")
    assert res.returncode == 0, "Visual regression exceeded threshold (see artifacts/*)"

    browser.close()
