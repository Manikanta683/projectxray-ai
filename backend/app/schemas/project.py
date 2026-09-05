from pydantic import BaseModel, Field


class ProjectIdeaRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=120)
    description: str = Field(..., min_length=20, max_length=5000)
    target_users: str = Field(..., min_length=3, max_length=1000)
    technologies: list[str] = Field(default_factory=list, max_length=30)


class DimensionScore(BaseModel):
    score: int = Field(..., ge=0, le=100)
    level: str
    reasons: list[str]


class RiskFlag(BaseModel):
    category: str
    severity: str
    message: str


class AnalysisResponse(BaseModel):
    project_title: str
    overall_score: int = Field(..., ge=0, le=100)
    verdict: str
    confidence: int = Field(..., ge=0, le=100)
    feasibility: DimensionScore
    technical_risk: DimensionScore
    originality: DimensionScore
    scope_clarity: DimensionScore
    user_fit: DimensionScore
    risk_flags: list[RiskFlag]
    recommendations: list[str]
    recommendation_source: str = "Rule-based fallback"
