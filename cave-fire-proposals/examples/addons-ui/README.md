Add‑Ons UI Example

This is a zero-build static example that loads the repository seed file `seeds/add_ons.json` and demonstrates quantity editing, per-line tax rounding, totals, and CSV export.

How to run locally

1. From the repository root run a simple static server (example using Python):

   python3 -m http.server 8000

2. Open the example page in your browser:

   http://localhost:8000/examples/addons-ui/

Notes

- The example loads `seeds/add_ons.json` via fetch, so it requires an HTTP server (not file://).
- Tax rate is editable at the top and defaults to 8.75%.
- Export CSV builds a simple CSV with per-line tax and totals.
