Cave Fire Proposals
====================

A small service and examples for composing fire protection proposals, computing totals with per-line rounding and tax, and exporting to HTML and DOCX.

Quick start
-----------

1. Install dependencies (recommended in a venv):

   python -m pip install --upgrade pip
   pip install -r requirements.txt
   pip install -r requirements-dev.txt

2. Run the API locally:

   python -m uvicorn app.server:app --reload

3. Endpoints

- POST /api/compose  — Accepts a proposal JSON payload and returns calculated totals.
- POST /api/export/html — Accepts proposal JSON and returns rendered HTML (Content-Type: text/html).
- POST /api/export/docx — Accepts proposal JSON and returns a DOCX file stream (Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document).

Example curl (HTML):

  curl -s -X POST http://localhost:8000/api/export/html \
     -H "Content-Type: application/json" \
     --data @seeds/default_proposal.json > proposal.html

Example curl (DOCX):

  curl -s -X POST http://localhost:8000/api/export/docx \
     -H "Content-Type: application/json" \
     --data @seeds/default_proposal.json --output proposal.docx

Local examples
--------------

- Static UI demo: open `examples/addons-ui/index.html` with a simple server: `python -m http.server 8000` and visit `http://localhost:8000/examples/addons-ui/`.
- React zero-build demo: open `examples/react-addons/index.html` the same way.

CI
--

The repository includes a GitHub Actions workflow (`.github/workflows/api-tests.yml`) that runs tests (including e2e Playwright tests) and generates export artifacts. On success the workflow uploads `proposal.html` and `proposal.docx` as artifacts for inspection.

E2E / browser tests
-------------------

We use Playwright for lightweight browser-driven end-to-end tests. To run them locally:

  # install dev dependencies and browsers once
  make install-dev

  # run the tests
  make e2e

Visual regression
-----------------

Visual regression snapshots are captured by the test suite and saved to `tests/e2e/baseline_screenshots/` on the first run. To enable automated comparisons in CI, commit a baseline image (e.g. `tests/e2e/baseline_screenshots/react_addons.png`). The CI job will capture a current screenshot and compare using `scripts/ci/compare_screenshots.py` (fails if difference exceeds 1% of pixels).

If a baseline does not exist the test will save the current screenshot as the baseline and skip the comparison (so you can review and commit the generated baseline for future runs).

When CI finds a visual diff
-------------------------

If the visual comparison finds a diff, the test creates `artifacts/react_addons_diff.png` and the CI job will fail and upload the `artifacts/` directory for inspection. To resolve:

1. Download the artifact and review `react_addons_diff.png` and `react_addons_current.png`.
2. If the change is expected, run the visual test locally to regenerate and inspect the new baseline, then commit `tests/e2e/baseline_screenshots/react_addons.png`.
3. If the change is unexpected, file an issue and attach the artifacts for debugging.

Baseline refresh job
--------------------

A scheduled CI job (`baseline-refresh`) runs weekly and captures an up-to-date screenshot and uploads it as `baseline_<runid>`. This helps maintainers review UI drift and decide whether to accept and commit baseline updates.

Caching Playwright browsers
---------------------------

The CI workflow includes a separate `playwright-setup` job which installs browsers and caches Playwright's browser files (`~/.cache/ms-playwright`) between runs to speed subsequent jobs. This should reduce job runtime after the first successful run.

Makefile & convenience
----------------------

Use `make install-dev` to install dev dependencies and Playwright browsers.
- `make start-api` — start the API server locally on port 8003
- `make start-static` — start the static server on port 8002
- `make start-servers` — quick reminder for starting both servers in separate terminals
- `make e2e` — run end-to-end tests
- `make gen-exports` — generate HTML & DOCX exports under `artifacts/`


Notes
-----

- Totals are computed by rounding each line item to cents and rounding tax per-line before summing (this is enforced in tests).
- Use `seeds/default_proposal.json` as a sample input for the export and compose endpoints.
