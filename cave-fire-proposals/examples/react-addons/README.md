React Add‑Ons Example

Zero-build: this example uses UMD React via CDN so no build step is required.

How to run

1. From repo root: python3 -m http.server 8000
2. Open: http://localhost:8000/examples/react-addons/

Notes

- The component fetches `seeds/add_ons.json` and shows interactive totals (tax rounding follows per-line cents rounding in back-end code).
- This is intended as a reference implementation to copy into your real app (React component).
