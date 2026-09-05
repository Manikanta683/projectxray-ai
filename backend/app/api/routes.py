from fastapi import APIRouter

from ..schemas.project import AnalysisResponse, ProjectIdeaRequest
from ..services.analyzer import analyze_project

router = APIRouter(prefix="/api/v1", tags=["analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
def analyze(project: ProjectIdeaRequest) -> AnalysisResponse:
    """Analyze a project idea and return explainable scores and recommendations."""
    return analyze_project(project)
