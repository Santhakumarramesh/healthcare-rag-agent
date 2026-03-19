# Startup Guide

## Entry Points

| Target | Command |
|--------|---------|
| **UI** | `streamlit run streamlit_app/app_healthcare.py --server.port 8501` |
| **API** | `uvicorn api.main:app --host 0.0.0.0 --port 8000` |

## Quick Start

```bash
# Terminal 1 - API
python run.py api

# Terminal 2 - UI
python run.py ui
```

Or use the shell scripts:

```bash
bash start_api.sh    # API on port 8000
bash start_healthcare.sh  # UI on port 8501
```

## Render (Production)

`render.yaml` uses explicit commands (no bash scripts):

- **API**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- **UI**: `streamlit run streamlit_app/app_healthcare.py --server.port $PORT --server.headless true --server.enableCORS false --server.enableXsrfProtection false --server.address 0.0.0.0`

## Docker

```bash
docker-compose up --build
```

- API: http://localhost:8000
- UI: http://localhost:8501
