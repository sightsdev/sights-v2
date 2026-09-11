# SIGHTS v2

> [!WARNING]
> SIGHTS v2 is still in beta\
> Expect bugs and breaking changes untill a stable release

The next generation of the [SIGHTS](https://github.com/sightsdev/sights) Project, redesigned from the ground up to address the steep learning curve, outdated framework and difficult extensibility of original SIGHTS.

It presently makes a number of core design decisions different to SIGHTS including a purely declarative semi-stateless model based on a single hardware configuration file, RESTful APIs instead of WebSockets, and recurring API calls instead of streaming of sensor data. Some of these decisions may change before the final version.

Build on a modern stack: Svelte (with tailwindcss) on the frontend and Starlette/FastAPI (Python) on the backend. The frontend uses endpoints generated from the backend using openapi.

### Docs

Documentation is available [here](https://sightsdev.github.io/docs/sights).

### Quick start

**Prerequisites**
- Python 3.13+
- NodeJS 22+
- [uv](https://docs.astral.sh/uv/)
- Familiarity with both Python and modern JavaScript environments will be helpful.

This repository contains both the frontend (`/src`) in React/Typescript and the backend (`/server`) in Python.

#### Backend (FastAPI)

The backend uses [Python virtual environments](https://docs.python.org/3/library/venv.html).

```bash
# From the repo root
cd server
uv sync

# Run the API (http://127.0.0.1:8000)
uv run uvicorn server:app --reload --host 127.0.0.1 --port 8000
```

#### Frontend (Svelte)

```bash
# In a separate terminal, still at repo root
yarn install
yarn run sights:dev
```

- The dev server runs on `http://localhost:3000` and forwards `/api/*` to `http://127.0.0.1:8000`.


#### Production build

```bash
yarn build
# Start the backend from the `server` directory as above; FastAPI serves the static build mounted at '/'
```

That’s it — backend on `:8000`, frontend on `:3000` (dev) or served by FastAPI (prod).
