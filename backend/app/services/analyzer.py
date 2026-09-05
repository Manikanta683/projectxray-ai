import re

from ..schemas.project import AnalysisResponse, DimensionScore, ProjectIdeaRequest, RiskFlag
from .llm_recommendations import enhance_recommendations
from .recommendations import generate_recommendations


HIGH_RISK_PATTERNS = {
    "medical": ("Safety/compliance requirements may be substantial for health-related systems.", "high"),
    "healthcare": ("Health data and clinical workflows can introduce regulatory and validation requirements.", "high"),
    "payment": ("Payment workflows require strong security, fraud controls, and reliable transaction handling.", "high"),
    "financial": ("Financial workflows can require security, auditability, and domain-specific compliance.", "high"),
    "biometric": ("Biometric data is sensitive and needs careful privacy, security, and consent design.", "high"),
    "face recognition": ("Face recognition introduces privacy, bias, accuracy, and consent risks.", "high"),
    "autonomous": ("Autonomous behavior increases testing, safety, and failure-mode complexity.", "high"),
    "real-time": ("Real-time requirements increase infrastructure and reliability complexity.", "medium"),
    "blockchain": ("Blockchain adds architecture, security, and operational complexity that must be justified.", "medium"),
    "drone": ("Hardware, control, safety, and field-testing requirements can increase delivery risk.", "high"),
    "iot": ("IoT projects add device, networking, deployment, and observability complexity.", "medium"),
    "critical infrastructure": ("Critical systems require unusually strong reliability, security, and validation.", "high"),
}

GENERIC_CATEGORIES = {
    "chatbot": "Chatbot is a crowded project category; differentiation should be explicit.",
    "e-commerce": "E-commerce is a common project category; focus on a distinctive workflow or niche.",
    "social media": "Social media is broad and crowded; narrow the user problem and core loop.",
    "attendance": "Attendance systems are common; identify a measurable improvement over existing tools.",
    "todo": "Task-management apps are common; add a specific user problem or measurable outcome.",
    "portfolio": "Portfolio systems are common; target a specific audience or unique outcome.",
}

COMMON_TECH = {
    "python", "fastapi", "flask", "django", "javascript", "typescript", "react", "next.js",
    "node", "node.js", "postgresql", "mysql", "mongodb", "sqlite", "docker", "streamlit",
    "scikit-learn", "pytorch", "tensorflow", "redis", "git", "github", "html", "css",
}


def clamp(value: float) -> int:
    return max(0, min(100, round(value)))


def score_level(score: int) -> str:
    if score >= 80:
        return "Strong"
    if score >= 65:
        return "Good"
    if score >= 50:
        return "Needs refinement"
    if score >= 35:
        return "Weak"
    return "Critical"


def risk_level(score: int) -> str:
    if score >= 80:
        return "Low concern"
    if score >= 65:
        return "Moderate concern"
    if score >= 45:
        return "High concern"
    return "Critical concern"


def words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+(?:[-'][a-z0-9]+)*", text.lower()))


def analyze_project(project: ProjectIdeaRequest) -> AnalysisResponse:
    title = project.title.strip()
    description = project.description.strip()
    users = project.target_users.strip()
    text = f"{title} {description} {users}".lower()
    tokens = words(text)
    tech = {item.strip().lower() for item in project.technologies if item.strip()}

    feasibility = 55.0
    feasibility_reasons: list[str] = []
    if len(description) >= 120:
        feasibility += 12
        feasibility_reasons.append("The description provides enough detail to begin defining an MVP.")
    elif len(description) < 60:
        feasibility -= 15
        feasibility_reasons.append("The idea is under-specified; the first release needs a clearer scope.")
    else:
        feasibility_reasons.append("The idea has a basic description, but the MVP boundary should be clearer.")
    if tech:
        feasibility += min(10, len(tech) * 2)
        feasibility_reasons.append("A technology stack is identified, reducing initial implementation uncertainty.")
    else:
        feasibility -= 8
        feasibility_reasons.append("No technology stack was supplied, so implementation assumptions remain uncertain.")
    if len(description) > 1200:
        feasibility -= 8
        feasibility_reasons.append("The description is broad; splitting it into an MVP and later phases would reduce delivery risk.")
    feasibility = clamp(feasibility)

    risk_points = 18.0
    risk_reasons: list[str] = []
    risk_flags: list[RiskFlag] = []
    for pattern, (message, severity) in HIGH_RISK_PATTERNS.items():
        if pattern in text:
            risk_points += 12 if severity == "high" else 7
            risk_flags.append(RiskFlag(category="technical/domain", severity=severity, message=message))
    unknown_tech = sorted(tech - COMMON_TECH)
    if unknown_tech:
        risk_points += min(15, len(unknown_tech) * 3)
        risk_reasons.append("Some technologies are not in the built-in common-stack list and should be validated early: " + ", ".join(unknown_tech[:5]) + ".")
    else:
        risk_reasons.append("The supplied stack uses broadly established technologies or no unusual dependencies were detected.")
    if any(term in tokens for term in {"production", "millions", "global", "24/7"}):
        risk_points += 10
        risk_flags.append(RiskFlag(category="scale", severity="medium", message="The stated scale or availability target may require architecture and operations beyond a simple MVP."))
    risk_score = clamp(100 - min(100, risk_points))
    if risk_flags:
        risk_reasons.insert(0, f"Detected {len(risk_flags)} requirement area(s) that deserve explicit risk validation.")
    else:
        risk_reasons.insert(0, "No major high-risk domain signals were detected in the supplied description.")

    generic_matches = [category for category in GENERIC_CATEGORIES if category in text]
    originality = 58.0
    originality_reasons: list[str] = []
    if generic_matches:
        originality -= min(30, len(generic_matches) * 12)
        originality_reasons.append("The idea overlaps with common project categories: " + ", ".join(generic_matches) + ".")
    else:
        originality += 12
        originality_reasons.append("The idea does not strongly match the built-in common project categories.")
    if len(users) >= 40:
        originality += 10
        originality_reasons.append("A reasonably specific target-user description provides room for differentiation.")
    else:
        originality -= 5
        originality_reasons.append("The target-user description is broad; a narrower user segment would improve differentiation.")
    if len(tech) >= 2 and len(description) >= 150:
        originality += 5
        originality_reasons.append("The combination of a defined stack and detailed concept supports a more specific product angle.")
    originality = clamp(originality)

    scope = 45.0
    scope_reasons: list[str] = []
    action_count = len(tokens & {"build", "create", "develop", "design", "automate", "predict", "detect", "track", "analyze", "manage", "recommend"})
    if action_count >= 2:
        scope += 12
        scope_reasons.append("The description states multiple concrete actions the system should perform.")
    if len(description) >= 120:
        scope += 10
    if len(description) > 900:
        scope -= 15
        scope_reasons.append("The description is large enough that scope creep is a concern; define must-have and later features.")
    if len(description) < 100:
        scope -= 10
        scope_reasons.append("The MVP boundary is not yet explicit from the description.")
    scope = clamp(scope)
    if not scope_reasons:
        scope_reasons.append("The scope is moderately defined, but the MVP should be expressed as one measurable outcome.")

    user_fit = 50.0
    user_fit_reasons: list[str] = []
    if len(users) >= 80:
        user_fit += 25
        user_fit_reasons.append("The target-user definition is detailed enough to support focused validation.")
    elif len(users) >= 40:
        user_fit += 15
        user_fit_reasons.append("The target-user definition is reasonably specific.")
    else:
        user_fit -= 10
        user_fit_reasons.append("The target-user definition is short; identify who has the problem and why they would use the product.")
    if any(word in tokens for word in {"problem", "pain", "need", "challenge", "save", "reduce", "improve"}):
        user_fit += 8
        user_fit_reasons.append("The description contains signals of a user problem or desired outcome.")
    else:
        user_fit_reasons.append("A concrete user problem or measurable outcome is not yet explicit.")
    user_fit = clamp(user_fit)

    overall = clamp(
        feasibility * 0.28
        + risk_score * 0.22
        + originality * 0.20
        + scope * 0.15
        + user_fit * 0.15
    )
    confidence = clamp(45 + min(25, len(description) // 50) + min(15, len(users) // 20) + min(15, len(tech) * 3))

    if overall >= 80:
        verdict = "Strong starting point"
    elif overall >= 65:
        verdict = "Promising, but needs refinement"
    elif overall >= 50:
        verdict = "Needs significant refinement"
    else:
        verdict = "High-risk concept that needs redesign"

    base_recommendations = generate_recommendations(
        text=text,
        technologies=tech,
        feasibility=feasibility,
        originality=originality,
        scope=scope,
        user_fit=user_fit,
        risk_points=risk_points,
        risk_flags=risk_flags,
        unknown_tech=unknown_tech,
    )

    analysis_snapshot = {
        "overall_score": overall,
        "verdict": verdict,
        "confidence": confidence,
        "feasibility": feasibility,
        "technical_risk": risk_score,
        "originality": originality,
        "scope_clarity": scope,
        "user_fit": user_fit,
        "risk_flags": [flag.model_dump() for flag in risk_flags],
    }
    enhanced_recommendations, recommendation_source = enhance_recommendations(
        project={"title": title, "description": description, "target_users": users, "technologies": sorted(tech)},
        analysis=analysis_snapshot,
        base_recommendations=base_recommendations,
    )

    return AnalysisResponse(
        project_title=title,
        overall_score=overall,
        verdict=verdict,
        confidence=confidence,
        feasibility=DimensionScore(score=feasibility, level=score_level(feasibility), reasons=feasibility_reasons),
        technical_risk=DimensionScore(score=risk_score, level=risk_level(risk_score), reasons=risk_reasons),
        originality=DimensionScore(score=originality, level=score_level(originality), reasons=originality_reasons),
        scope_clarity=DimensionScore(score=scope, level=score_level(scope), reasons=scope_reasons),
        user_fit=DimensionScore(score=user_fit, level=score_level(user_fit), reasons=user_fit_reasons),
        risk_flags=risk_flags,
        recommendations=enhanced_recommendations,
        recommendation_source=recommendation_source,
    )
