# ProjectX-Ray

Explainable system that stress-tests software project ideas for feasibility, technical risk, originality, scope clarity, target-user fit, and improvement opportunities.

## Current Status

**Phase 3: Live project analysis demo — v0.4.0**

- FastAPI analysis backend
- Explainable scoring across five dimensions
- Context-aware recommendations
- Domain-specific risk flags
- Live Streamlit demonstration frontend
- Screenshot-ready demo project preloaded
- Automated backend tests
- GitHub Actions CI

The analysis engine is deterministic and transparent. Scores are screening signals, not proof of product-market fit or technical success.

## Run the backend

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

API documentation: `http://127.0.0.1:8000/docs`

## Run the live frontend

Open a second terminal from the repository root:

```powershell
cd frontend
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The frontend calls the FastAPI backend automatically. Keep the backend running while demonstrating the dashboard.

To use a deployed backend, set `PROJECTXRAY_API_URL` to the backend base URL before starting Streamlit.

## Live recommendation demo

The frontend includes the project shown in the demonstration:

**AI Project Idea Generator & Mentor for Final-Year Projects**

> Build an AI-powered platform that helps final-year students generate project ideas based on their interests and skills and provides guidance on features, technologies, development steps, and improvements to turn the idea into a practical project.

When the inputs change, ProjectX-Ray sends the current project to `/api/v1/analyze` and refreshes the recommendations. For this example, the engine can recommend personalization inputs, idea-ranking criteria, an actionable mentor flow, a curated project knowledge base, MVP definition, and student pilot validation.

## API

### POST `/api/v1/analyze`

The response contains:

- overall score and verdict
- confidence estimate
- feasibility score and reasons
- technical-risk score and risk flags
- originality score and reasons
- scope-clarity score and reasons
- target-user fit score and reasons
- context-aware recommendations

## Roadmap

1. Evidence-backed originality/similarity analysis
2. Project risk matrix with priority and impact
3. Explainable report generation
4. Historical project benchmarking
5. Optional model-assisted critique
6. Deployment and monitoring
