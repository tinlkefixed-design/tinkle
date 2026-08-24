# Tinkle React 3D Client (experimental, standalone)

This is an alternative, standalone 3D front-end built with React Three Fiber.
It is **not** the client served by the backend at `/` — that is the
production UI in `../tinkle/ui` (vanilla JS), wired directly into
`tinkle/api/main.py`. This React client is a separate dev tool for
prototyping richer 3D interactions against the same `/api/v1/visual3d`
endpoints; it is not mounted by FastAPI and must be run on its own.

## Run

```bash
npm install
npm run dev        # http://localhost:5173, proxies /api to the backend on :8000
```

Run the backend first in another terminal:

```bash
uvicorn tinkle.api.main:app --reload
```

## Build

```bash
npm run build       # type-checks then outputs static files to ../dist
```
