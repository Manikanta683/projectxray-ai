# ProjectX-Ray

Explainable system that stress-tests software project ideas for feasibility, technical risk, originality, and improvement opportunities.

## Current Status

Phase 1: Working backend MVP

- FastAPI backend
- Health check endpoint
- Structured project idea input
- Feasibility scoring
- Technical risk scoring
- Originality scoring
- Explainable reasons
- Improvement recommendations
- Automated tests

## Backend

Run locally from the repository root:

```bash
cd backend
python -m venv venv
```

### Windows PowerShell

```powershell
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### macOS / Linux

```bash
source venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

API documentation:

`http://127.0.0.1:8000/docs`

## API

### POST `/api/v1/analyze`

Example request:

```json
{
  "title": "Campus Study Planner",
  "description": "A web application that helps college students plan study sessions, track tasks, and review weekly progress.",
  "target_users": "College students who need a simple study planning tool",
  "technologies": ["Python", "FastAPI", "React", "PostgreSQL"]
}
```

The response contains an overall score, feasibility, technical-risk and originality assessments, reasons, and recommendations.

## Testing

From `backend` with the virtual environment activated:

```bash
python -m pytest -q
```

## Roadmap

1. Strengthen rule-based risk engine
2. Add structured project assessment dimensions
3. Add evidence-backed originality/similarity analysis
4. Add explainable analysis report generation
5. Build frontend dashboard
6. Add optional LLM-assisted critique
7. Add deployment and CI/CD
