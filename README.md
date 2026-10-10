# INDUX-OS — Industrial Intelligence Command Center

A competition/demo-oriented prototype for Team Reborn Innovators.

## What's improved
- Responsive, premium industrial command-center interface.
- Clear demo/prototype labels so randomized values are not mistaken for live plant telemetry.
- SOP query interface with source/manual/page fields and no-match behavior.
- 23 clickable capability modules, deployment checklist, activity stream and visual demo signals.
- Frontend and FastAPI endpoint paths are aligned (`POST /api/module/{name}`).
- API health endpoint (`GET /api/health`) and OpenAPI docs (`/docs`).
- Basic input length validation and explicit warning language for safety-critical work.

## Run locally
Backend:
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
Open `index.html` with a local static server and set the API URL with a query string:
`http://localhost:5500/?api=http://127.0.0.1:8000`

## Deploy
- Deploy `backend/` as a Python FastAPI service on Render (start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`).
- Host `index.html` as a static site on Vercel.
- In `index.html`, update the `BACKEND` fallback URL to the exact deployed backend URL, or open the frontend with `?api=https://YOUR-BACKEND-DOMAIN`.
- Before production, replace `allow_origins=["*"]` with your exact frontend origin and add authentication, rate limiting, monitoring and secrets management.

## Important limitations
This is a polished prototype, not a production-ready industrial AI product. The SOP library is five illustrative records; retrieval is keyword-based, not vector RAG. Capability modules mostly return simulated/demo values. There is no live sensor, robot, camera, satellite, health, ERP, or LLM integration. Do not use demo outputs to operate machinery or make safety-critical decisions. For a credible competition pitch, present a live end-to-end workflow and measured results, and clearly separate implemented features from roadmap items.

## v3 — Winning-demo upgrades
- **Live predictive loop**: simulated vibration stream -> backend `POST /api/analyze` (EWMA z-score, trend, time-to-limit) -> automatic SOP match -> auto-drafted work order with LOTO/approval gate.
- SOP library grown to 9 records; Hinglish synonym expansion (garam, awaaz, tel, risaav...); keyword match strength returned.
- Impact estimator (user assumptions, clearly labelled not measured).
- API status pill (Render free tier may need ~30-50s to wake: open `/api/health` before presenting).
- Pitch tip: say "simulated stream, real analytics" — judges reward honesty plus a working end-to-end flow.

## v4 — Real documents & real data
- **Real PDF RAG**: `backend/sop_library/` holds 9 generated sample SOP PDFs, parsed with pypdf at startup; upload your own PDFs from the UI. BM25 retrieval, page-level citations, refusal when no confident match.
- **LLM answers (optional)**: set `ANTHROPIC_API_KEY` (and optionally `LLM_MODEL`) on Render; answers are then written strictly from retrieved excerpts with [n] citations. Without a key, the top excerpt is returned extractively.
- **Real data**: upload `sample_data/plant_log.csv` (or your own) in Advanced Features; or push readings via `POST /api/sensor` / `sensor_client.py` (serial Arduino/ESP32 supported).
- Home = SOP Co-pilot (team focus). Advanced Features = CSV/sensor analytics for machine, energy, safety, water and vitals profiles, predictive loop, impact estimator and capability lab.
- Uploaded documents and sensor buffers live in server memory (reset on restart) — add a database for persistence.
- Not covered yet: multimodal image/diagram understanding, voice input, auth. Present these as roadmap.

## v5 — Voice & image
- **Voice**: mic button (English / Hindi) uses the browser Web Speech API (Chrome/Edge, HTTPS); answers can be read aloud. Audio is processed by the browser vendor's speech service.
- **Image**: upload or capture a photo/diagram -> `POST /api/vision` -> Claude vision describes what is visible and extracts keywords -> BM25 search over indexed SOP PDFs with page citations. Requires `ANTHROPIC_API_KEY` on the backend; without it the endpoint says so.
- Not yet: images embedded inside PDFs are not indexed; no wake-word or offline speech.

## v6 — Advanced Features suites (home page stays the SOP co-pilot)
- Vision (defect / aerial / checkout) via `/api/inspect` (needs `ANTHROPIC_API_KEY`); defect Pareto kept per session.
- Change detection (two images, in-browser pixel diff, area estimate).
- Digital-twin line what-if (bottleneck + utilisation model, in-browser).
- Demand forecast + price advisor (`/api/forecast`), energy optimiser (`/api/energy`), OT-traffic anomaly profile in the CSV engine.
- Agentic workflow with human approval + audit log (`/api/workflow`; ERP/email connectors are simulated).
- Multilingual assistant for farmer / citizen / patient-summary use (`/api/assist`, needs key).
- Not built: robot navigation/SLAM, pick-and-place control, deepfake detection, satellite/GIS hazard models — roadmap only.
- Samples: `sample_data/sales_log.csv`, `energy_hourly.csv`, `ot_traffic.csv`, `plant_log.csv`.


## v7 — Judge Mode & evidence pack
- Added `GET /api/evaluate`, a deterministic, nine-query source-retrieval smoke test using the currently indexed PDF chunks.
- Added a Judge Mode panel showing source recall@3, mean reciprocal rank, expected-vs-matched source and benchmark limitations.
- Added JSON export for raw benchmark output and a competition brief.
- Important: these are internal smoke-test measures only. They do not prove answer correctness, safety or real-world impact. Use the actual approved SOP library and a held-out evaluation set before making accuracy claims.
