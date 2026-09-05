from app.services.analyzer import analyze_project
from app.schemas.project import ProjectIdeaRequest


def test_project_analysis_returns_rich_scores_and_contextual_recommendation():
    project = ProjectIdeaRequest(
        title="Campus Study Planner",
        description="A web application that helps college students plan study sessions, track tasks, and review weekly progress with reminders and simple analytics.",
        target_users="College students who need a simple study planning tool for organizing their weekly study workload",
        technologies=["Python", "FastAPI", "React", "PostgreSQL"],
    )

    result = analyze_project(project)

    assert 0 <= result.overall_score <= 100
    assert 0 <= result.confidence <= 100
    assert 0 <= result.feasibility.score <= 100
    assert 0 <= result.technical_risk.score <= 100
    assert 0 <= result.originality.score <= 100
    assert 0 <= result.scope_clarity.score <= 100
    assert 0 <= result.user_fit.score <= 100
    assert result.recommendations
    assert any("students" in item.lower() for item in result.recommendations)


def test_high_risk_project_gets_risk_flags_and_domain_recommendations():
    project = ProjectIdeaRequest(
        title="Medical Face Recognition Platform",
        description="A real-time healthcare platform using face recognition and biometric data to identify patients and automate clinical workflows.",
        target_users="Hospitals and clinical staff",
        technologies=["Python", "FastAPI"],
    )

    result = analyze_project(project)

    assert result.risk_flags
    assert any(flag.severity == "high" for flag in result.risk_flags)
    assert result.technical_risk.score < 80
    assert any("privacy" in item.lower() or "consent" in item.lower() for item in result.recommendations)


def test_generic_project_gets_differentiation_feedback():
    project = ProjectIdeaRequest(
        title="Student Chatbot",
        description="A chatbot that answers common student questions and provides basic information through a web application.",
        target_users="Students",
        technologies=["Python", "FastAPI"],
    )

    result = analyze_project(project)

    assert result.originality.score < 70
    assert any("differentiator" in item.lower() for item in result.recommendations)


def test_payment_project_gets_security_recommendations():
    project = ProjectIdeaRequest(
        title="Student Wallet",
        description="A payment platform for students to make financial transactions and manage campus purchases.",
        target_users="College students making frequent campus purchases",
        technologies=["Python", "FastAPI", "React", "PostgreSQL"],
    )

    result = analyze_project(project)

    assert any("authentication" in item.lower() or "audit" in item.lower() for item in result.recommendations)
    assert any("transaction" in item.lower() or "fraud" in item.lower() for item in result.recommendations)
