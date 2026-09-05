# ProjectX-Ray

> Explainable project stress-testing for feasibility, technical risk, originality, scope clarity, target-user fit, and practical improvements.

## 🚀 Live Demo

- **Frontend:** https://projectxray-demo.onrender.com
- **Backend API:** https://projectxray-api.onrender.com
- **API health:** https://projectxray-api.onrender.com/health
- **Interactive API docs:** https://projectxray-api.onrender.com/docs

ProjectX-Ray is deployed as two Render web services: a Streamlit dashboard for the user experience and a FastAPI backend for project analysis. Both services deploy automatically from the `main` branch.

## What it does

ProjectX-Ray takes a software project idea and produces an explainable screening report instead of an unexplained yes/no answer.

It evaluates five dimensions:

1. **Feasibility** — whether the idea is practical with the stated scope and technologies.
2. **Technical risk** — domain and implementation risks that may make the project harder to deliver safely or reliably.
3. **Originality** — how differentiated the idea appears from generic/common project patterns.
4. **Scope clarity** — whether the problem, action, MVP boundary, and implementation direction are clear.
5. **Target-user fit** — whether the intended users are specific enough for meaningful project validation.

The system also generates **context-aware recommendations** and **domain-specific risk flags**.

## Current status

**Live deployment — v0.5.0**

- FastAPI analysis backend
- Streamlit live dashboard
- Explainable scoring across five dimensions
- Context-aware recommendations
- Domain-specific risk flags
- Screenshot-ready demo project
- Automated backend tests
- GitHub Actions CI
- Render deployment for frontend and backend
- Automatic deployment from `main`
- Deterministic and transparent analysis engine

> Scores are screening signals. They are not proof of product-market fit, originality, technical success, or project completion.

## Architecture

```text
User
  |
  v
Streamlit Dashboard
  |
  |  POST /api/v1/analyze
  v
FastAPI Backend
  |
  +--> Project analysis
  +--> Risk scoring
  +--> Recommendation engine
  |
  v
Explainable analysis report
```

### Deployment architecture

```text
GitHub: main
     |
     +--------------------+
     |                    |
     v                    v
Render API            Render Demo
FastAPI               Streamlit
     |                    |
     +-------- HTTPS -----+
          API calls
```

The Streamlit frontend sends analysis requests from the server to the FastAPI service using `PROJECTXRAY_API_URL`.

## Run locally

### 1. Backend

From the repository root:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Backend documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

### 2. Frontend

Open a second PowerShell terminal:

```powershell
cd frontend
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open:

```text
http://localhost:8501
```

By default the frontend calls `http://127.0.0.1:8000`.

To use another backend:

```powershell
$env:PROJECTXRAY_API_URL="https://projectxray-api.onrender.com"
python -m streamlit run app.py
```

## Demo project

The dashboard is preloaded with a final-year project example:

**AI Project Idea Generator & Mentor for Final-Year Projects**

> Build an AI-powered platform that helps final-year students generate project ideas based on their interests and skills and provides guidance on features, technologies, development steps, and improvements to turn the idea into a practical project.

Use **Load screenshot project** in the sidebar to restore the prepared example.

For this example, ProjectX-Ray can recommend personalization inputs, idea-ranking criteria, an actionable mentor flow, a curated project knowledge base, MVP definition, and student pilot validation.

## API

### `POST /api/v1/analyze`

Example request:

```json
{
  "title": "Project title",
  "description": "What the project will build and how it will be used.",
  "target_users": "Specific target users",
  "technologies": ["Python", "FastAPI"]
}
```

The response includes:

- overall score and verdict
- analysis confidence
- feasibility score and reasons
- technical-risk score and risk flags
- originality score and reasons
- scope-clarity score and reasons
- target-user-fit score and reasons
- context-aware recommendations

## Deployment

Render configuration is maintained in [`render.yaml`](render.yaml).

The repository defines:

- **API service:** `projectxray-api`
  - FastAPI
  - Python
  - health endpoint: `/health`
- **Demo service:** `projectxray-demo`
  - Streamlit
  - connects to the API through `PROJECTXRAY_API_URL`

Both services use the `main` branch and are configured for automatic deployment.

The repository also contains root-level compatibility files so the existing Render API service can start the backend even when its service root directory is the repository root.

## Testing

Run the backend tests locally:

```powershell
cd backend
python -m pytest -q
```

CI runs the same backend test suite on pushes and pull requests targeting `main`.

## Project structure

```text
projectxray-ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── app.py
│   └── requirements.txt
├── data/
│   └── README.md
├── docs/
│   ├── architecture.md
│   └── methodology.md
├── app/
│   └── main.py
├── .env.example
├── .gitignore
├── .python-version
├── LICENSE
├── main.py
├── render.yaml
├── requirements.txt
└── README.md
```

## Roadmap

1. Evidence-backed originality and similarity analysis
2. Project risk matrix with priority and impact
3. Explainable report generation
4. Historical project benchmarking
5. Optional model-assisted critique
6. Deployment monitoring and analytics

## Important note

ProjectX-Ray is designed as a decision-support and project-screening tool. Its deterministic analysis makes the reasoning visible, but the result should be reviewed by the project team before making high-impact technical or business decisions.
