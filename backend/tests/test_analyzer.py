from app.services.analyzer import analyze_project
from app.schemas.project import ProjectIdeaRequest


def test_project_analysis_returns_scores():
    project = ProjectIdeaRequest(
        title="Campus Study Planner",
        description="A web application that helps college students plan study sessions, track tasks, and review weekly progress.",
        target_users="College students who need a simple study planning tool",
        technologies=["Python", "FastAPI", "React", "PostgreSQL"],
    )

    result = analyze_project(project)

    assert 0 <= result.overall_score <= 100
    assert 0 <= result.feasibility.score <= 100
    assert 0 <= result.technical_risk.score <= 100
    assert 0 <= result.originality.score <= 100
    assert result.recommendations
