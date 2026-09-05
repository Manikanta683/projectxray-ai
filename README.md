# ProjectX-Ray

Explainable system that stress-tests software project ideas for feasibility, technical risk, originality, and improvement opportunities.

## Current Status

Phase 1: Backend foundation

- FastAPI backend
- Health check endpoint
- Structured project architecture

## Backend

Run locally:

```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API documentation will be available at `http://127.0.0.1:8000/docs`.

## Roadmap

1. Project idea input schema
2. Feasibility scoring
3. Technical risk scoring
4. Originality analysis
5. Improvement recommendations
6. Explainable analysis report
7. Frontend dashboard
