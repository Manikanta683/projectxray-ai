from fastapi import FastAPI

from .api.routes import router as analysis_router

APP_VERSION = "0.5.0"

app = FastAPI(
    title="ProjectX-Ray API",
    description="Explainable project feasibility, risk, originality and improvement analysis system",
    version=APP_VERSION,
)

app.include_router(analysis_router)


@app.get("/")
def root():
    return {
        "project": "ProjectX-Ray",
        "status": "running",
        "version": APP_VERSION,
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
    return {"status": "healthy", "version": APP_VERSION}
