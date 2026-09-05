from fastapi import FastAPI

from .api.routes import router as analysis_router

app = FastAPI(
    title="ProjectX-Ray API",
    description="Project feasibility, risk, originality and improvement analysis system",
    version="0.2.0",
)

app.include_router(analysis_router)


@app.get("/")
def root():
    return {
        "project": "ProjectX-Ray",
        "status": "running",
        "version": "0.2.0",
        "analysis_endpoint": "/api/v1/analyze",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
