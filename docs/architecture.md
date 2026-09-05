# ProjectX-Ray Architecture

ProjectX-Ray uses a small, modular architecture so the analysis engine stays transparent, testable, and easy to extend.

## Runtime architecture

```text
User
  |
  v
Streamlit Dashboard
  |
  | POST /api/v1/analyze
  v
FastAPI API
  |
  +--> Project analysis service
  +--> Risk scoring / dimension scoring
  +--> Recommendation service
  |
  v
Explainable AnalysisResponse
```

## Deployment architecture

```text
GitHub main branch
       |
       +-------------------------+
       |                         |
       v                         v
projectxray-api             projectxray-demo
Render Web Service          Render Web Service
FastAPI                     Streamlit
       ^                         |
       |                         |
       +------ HTTPS API --------+
```

The frontend uses the `PROJECTXRAY_API_URL` environment variable to locate the FastAPI backend. In the deployed environment it points to `https://projectxray-api.onrender.com`.

## Backend modules

- `backend/app/api/` — HTTP routes.
- `backend/app/schemas/` — request and response models.
- `backend/app/services/analyzer.py` — deterministic project analysis and scoring.
- `backend/app/services/recommendations.py` — context-aware improvement recommendations.
- `backend/tests/` — automated backend tests.

## Design principle

The current MVP intentionally avoids an opaque model dependency. Each score is derived from explicit project signals and accompanied by reasons, risk flags, and recommendations. Advanced model-assisted or evidence-backed components can be added later without replacing the core API contract.
