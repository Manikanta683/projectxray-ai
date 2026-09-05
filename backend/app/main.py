from fastapi import FastAPI

from .api.routes import router as analysis_router

app = FastAPI(
    title="ProjectX-Ray API",
    description="Explainable project feasibility, risk, originality and improvement analysis system",
    version="0.3.0",
)

app.include_router(analysis_router)


@app.get("/")
def root():
    return {
        "project": "ProjectX-Ray",
        "status": "running",
        "version": "0.3.0",
        "capabilities": [
            "feasibility analysis",
            "technical risk analysis",
            "originality screening",
            "scope clarity analysis",
            "target-user fit analysis",
            "explainable recommendations",
        ],
    }


@app.get("/health")
def health():
    return {"status": "healthy", "version": "0.3.0"}
