from fastapi import FastAPI

app = FastAPI(
    title="ProjectX-Ray API",
    description="Project feasibility, risk, originality and improvement analysis system",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "project": "ProjectX-Ray",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
