# Pinch Router Lab Web

React + Vite UI for choosing a PinchBench case and watching the routed Agent in
real time.

Start the API in one terminal:

```bash
cd apps/api
uv run pinch-api
```

Start the UI in another:

```bash
cd apps/web
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. Vite proxies `/api` to the FastAPI backend on
port 8000, including the SSE event stream.
