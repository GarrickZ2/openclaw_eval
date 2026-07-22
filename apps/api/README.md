# Pinch API

FastAPI + SSE backend for the routed PinchBench demo.

```bash
cd apps/api
uv sync
uv run pinch-api
```

The API listens on `http://127.0.0.1:8000`.

```bash
curl http://127.0.0.1:8000/api/cases
curl -X POST http://127.0.0.1:8000/api/runs \
  -H 'content-type: application/json' \
  --data '{"case_id":"task_files","max_steps":8}'
curl -N http://127.0.0.1:8000/api/runs/<run_id>/events
```

Each run persists `run.json`, `events.jsonl`, and its isolated workspace under
`var/runs/<run_id>/`.
