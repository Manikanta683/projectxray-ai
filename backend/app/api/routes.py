from fastapi import APIRouter, HTTPException

from ..schemas.project import (
    AnalysisResponse,
    LoginRequest,
    LoginResponse,
    ProjectHistoryItem,
    ProjectIdeaRequest,
    RecommendationAgentRequest,
    RecommendationAgentResponse,
    RegisterRequest,
)
from ..services.analyzer import analyze_project
from ..services.auth import authenticate, ensure_demo_user, get_projects, register_user, save_project
from ..services.recommendation_agent import ask_agent

router = APIRouter(prefix="/api/v1", tags=["analysis"])
ensure_demo_user()


@router.post("/auth/login", response_model=LoginResponse)
def login(request: LoginRequest) -> LoginResponse:
    email = request.email.strip().lower()
    if authenticate(email, request.password):
        return LoginResponse(authenticated=True, user=email, message="Login successful")
    return LoginResponse(authenticated=False, user="", message="Invalid email or password")


@router.post("/auth/register", response_model=LoginResponse)
def register(request: RegisterRequest) -> LoginResponse:
    ok, message = register_user(request.email, request.password)
    email = request.email.strip().lower() if ok else ""
    return LoginResponse(authenticated=ok, user=email, message=message)


@router.post("/analyze", response_model=AnalysisResponse)
def analyze(project: ProjectIdeaRequest, email: str = "") -> AnalysisResponse:
    result = analyze_project(project)
    if email.strip():
        save_project(email, project.model_dump(), result.model_dump())
    return result


@router.get("/projects/{email}", response_model=list[ProjectHistoryItem])
def history(email: str) -> list[ProjectHistoryItem]:
    if "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid user email")
    return [ProjectHistoryItem(**item) for item in get_projects(email)]


@router.post("/recommend", response_model=RecommendationAgentResponse)
def recommend(request: RecommendationAgentRequest) -> RecommendationAgentResponse:
    answer, next_steps, source = ask_agent(
        project=request.project.model_dump(),
        analysis=request.analysis.model_dump(),
        question=request.question.strip(),
    )
    return RecommendationAgentResponse(answer=answer, next_steps=next_steps, source=source)
