from fastapi import APIRouter

from ..schemas.project import (
    AnalysisResponse,
    ProjectIdeaRequest,
    RecommendationAgentRequest,
    RecommendationAgentResponse,
)
from ..services.analyzer import analyze_project
from ..services.recommendation_agent import ask_agent

router = APIRouter(prefix="/api/v1", tags=["analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
def analyze(project: ProjectIdeaRequest) -> AnalysisResponse:
    """Analyze a project idea and return explainable scores and recommendations."""
    return analyze_project(project)


@router.post("/recommend", response_model=RecommendationAgentResponse)
def recommend(request: RecommendationAgentRequest) -> RecommendationAgentResponse:
    """Ask the live recommendation agent about an analyzed project."""
    answer, next_steps, source = ask_agent(
        project=request.project.model_dump(),
        analysis=request.analysis.model_dump(),
        question=request.question.strip(),
    )
    return RecommendationAgentResponse(answer=answer, next_steps=next_steps, source=source)
