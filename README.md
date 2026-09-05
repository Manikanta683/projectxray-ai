# ProjectX-Ray

Explainable system that stress-tests software project ideas for feasibility, technical risk, originality, scope clarity, target-user fit, and improvement opportunities.

## Current Status

**Phase 2: Explainable analysis engine — v0.3.0**

- FastAPI backend
- Structured project idea input
- Feasibility analysis
- Technical-risk analysis with risk flags
- Originality screening
- Scope-clarity analysis
- Target-user fit analysis
- Confidence estimate
- Explainable reasons for every score
- Prioritized recommendations
- Automated unit tests
- GitHub Actions CI

The current engine is deterministic and transparent. It does not pretend that keyword matching or heuristics prove feasibility or market demand. Scores are screening signals that can be extended with evidence and learned models later.

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
  "description": "A web application that helps college students plan study sessions, track tasks, and review weekly progress with reminders and simple analytics.",
  "target_users": "College students who need a simple study planning tool for organizing their weekly study workload",
  "technologies": ["Python", "FastAPI", "React", "PostgreSQL"]
}
```

The response contains:

- overall score and verdict
- confidence estimate
- feasibility score and reasons
- technical-risk score and risk flags
- originality score and reasons
- scope-clarity score and reasons
- target-user fit score and reasons
- actionable recommendations

## Analysis model

The engine combines several transparent signals:

1. **Feasibility** — description detail, stack definition, and scope breadth.
2. **Technical risk** — high-risk domain requirements, scale signals, and unfamiliar technology signals.
3. **Originality** — overlap with common project categories plus specificity of the target audience.
4. **Scope clarity** — concrete actions, description depth, and scope-breadth signals.
5. **User fit** — specificity of the target user and evidence of a problem or desired outcome.
6. **Confidence** — amount of information available to the analyzer; it is not model accuracy.

This is intentionally an explainable baseline. Future evidence-backed similarity analysis and optional model-assisted critique will be added as separate components.

## Testing

From `backend` with the virtual environment activated:

```bash
python -m pytest -q
```

## Roadmap

1. Evidence-backed originality/similarity analysis
2. Project risk matrix and severity prioritization
3. Explainable analysis report generation
4. Frontend dashboard
5. Optional LLM-assisted critique with structured outputs
6. Historical project benchmarking
7. Deployment and monitoring
