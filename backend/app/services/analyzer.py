import re

from ..schemas.project import AnalysisResponse, DimensionScore, ParameterScore, ProjectIdeaRequest, RiskFlag
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

PARAMETER_NAMES = [
    "Code Quality", "Security", "Efficiency", "Testing", "Accessibility", "Problem Statement Alignment"
]


def clamp(value: float) -> int:
    return max(0, min(100, round(value)))


def score_level(score: int) -> str:
    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Good"
    if score >= 55:
        return "Fair"
    if score >= 40:
        return "Needs improvement"
    return "Weak"


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


def _parameter(name: str, text: str, tokens: set[str], tech: set[str], description: str, users: str, risk_flags: list[RiskFlag]) -> ParameterScore:
    score = 50
    reasons: list[str] = []

    if name == "Code Quality":
        if any(t in tech for t in {"git", "github"}): score += 12; reasons.append("Version control is part of the stack.")
        if any(t in tech for t in {"python", "javascript", "typescript", "java", "c++", "c#"}): score += 8; reasons.append("A well-established programming language is specified.")
        if any(w in tokens for w in {"modular", "architecture", "component", "clean", "layered", "api"}): score += 18; reasons.append("The project description includes software-structure signals.")
        else: reasons.append("Modularity, architecture, naming, and maintainability are not explicit in the idea yet.")
        if len(tech) > 8: score -= 10; reasons.append("A large stack can increase integration complexity.")

    elif name == "Security":
        if any(w in tokens for w in {"security", "secure", "authentication", "authorization", "auth", "encryption", "privacy", "permission", "audit"}): score += 25; reasons.append("Security controls are explicitly considered.")
        else: reasons.append("Authentication, authorization, privacy, input validation, and secrets handling should be defined.")
        if any(f.severity == "high" for f in risk_flags): score -= 18; reasons.append("The detected domain risk requires stronger security controls and validation.")
        if any(t in tech for t in {"fastapi", "django", "flask"}): score += 5; reasons.append("The backend stack supports standard server-side security patterns.")

    elif name == "Efficiency":
        if any(w in tokens for w in {"performance", "optimize", "optimization", "cache", "caching", "async", "batch", "latency", "efficient"}): score += 25; reasons.append("Performance or efficient processing is explicitly addressed.")
        else: reasons.append("Performance targets, response time, and resource usage are not specified.")
        if "redis" in tech or "cache" in tokens: score += 10; reasons.append("Caching is available or considered.")
        if "real-time" in text or "real time" in text: score -= 10; reasons.append("Real-time requirements increase latency and concurrency pressure.")

    elif name == "Testing":
        if any(w in tokens for w in {"test", "testing", "pytest", "validation", "validate", "qa", "quality", "unit", "integration"}): score += 30; reasons.append("Testing or validation is explicitly mentioned.")
        else: reasons.append("Add unit, integration, validation, and failure-path tests with clear acceptance criteria.")
        if "pytest" in tech: score += 12; reasons.append("Pytest is specified for automated testing.")
        if risk_flags: score -= 10; reasons.append("Detected risks need dedicated negative-path and edge-case testing.")

    elif name == "Accessibility":
        if any(w in tokens for w in {"accessibility", "accessible", "wcag", "keyboard", "screen-reader", "screenreader", "contrast", "aria"}): score += 35; reasons.append("Accessibility requirements are explicitly included.")
        else: reasons.append("Keyboard navigation, readable contrast, labels, responsive layout, and assistive-technology support are not specified.")
        if any(t in tech for t in {"react", "next.js", "html", "css", "streamlit"}): score += 5; reasons.append("The UI stack can support accessible interface patterns.")

    elif name == "Problem Statement Alignment":
        if any(w in tokens for w in {"problem", "pain", "need", "challenge", "issue", "reduce", "improve", "save", "solution", "outcome"}): score += 25; reasons.append("The project connects the solution to a stated problem or outcome.")
        else: reasons.append("Clearly state the user problem, affected users, current pain, and intended outcome.")
        if len(users) >= 40: score += 12; reasons.append("The target users are specific enough to support focused validation.")
        else: reasons.append("The target audience should be narrowed to the people who experience the problem.")
        if any(w in tokens for w in {"measure", "metric", "kpi", "success", "goal"}): score += 13; reasons.append("A measurable success signal is mentioned.")
        else: reasons.append("Add a measurable success criterion for the proposed solution.")

    score = clamp(score)
    if not reasons:
        reasons.append("Score is based on the supplied project description, users, technology choices, and detected requirements.")
    return ParameterScore(name=name, score=score, level=score_level(score), reasons=reasons[:3])


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
        feasibility += 12; feasibility_reasons.append("The description provides enough detail to begin defining an MVP.")
    elif len(description) < 60:
        feasibility -= 15; feasibility_reasons.append("The idea is under-specified; the first release needs a clearer scope.")
    else:
        feasibility_reasons.append("The idea has a basic description, but the MVP boundary should be clearer.")
    if tech:
        feasibility += min(10, len(tech) * 2); feasibility_reasons.append("A technology stack is identified, reducing initial implementation uncertainty.")
    else:
        feasibility -= 8; feasibility_reasons.append("No technology stack was supplied, so implementation assumptions remain uncertain.")
    if len(description) > 1200:
        feasibility -= 8; feasibility_reasons.append("The description is broad; split it into an MVP and later phases.")
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
    risk_score = clamp(100 - min(100, risk_points))
    risk_reasons.insert(0, f"Detected {len(risk_flags)} requirement area(s) that deserve explicit risk validation." if risk_flags else "No major high-risk domain signals were detected in the supplied description.")

    generic_matches = [category for category in GENERIC_CATEGORIES if category in text]
    originality = 58.0
    originality_reasons: list[str] = []
    if generic_matches:
        originality -= min(30, len(generic_matches) * 12); originality_reasons.append("The idea overlaps with common project categories: " + ", ".join(generic_matches) + ".")
    else:
        originality += 12; originality_reasons.append("The idea does not strongly match the built-in common project categories.")
    if len(users) >= 40: originality += 10; originality_reasons.append("A reasonably specific target-user description provides room for differentiation.")
    else: originality -= 5; originality_reasons.append("The target-user description is broad; a narrower user segment would improve differentiation.")
    originality = clamp(originality)

    scope = 50.0
    scope_reasons: list[str] = []
    if len(description) >= 120: scope += 15
    if len(description) > 900: scope -= 20; scope_reasons.append("The description is broad; define must-have and later features.")
    if len(description) < 100: scope -= 12; scope_reasons.append("The MVP boundary is not explicit.")
    if any(w in tokens for w in {"mvp", "minimum", "first version", "phase 1"}): scope += 15; scope_reasons.append("An MVP or phased delivery approach is described.")
    if not scope_reasons: scope_reasons.append("Keep the first release focused on one measurable outcome.")
    scope = clamp(scope)

    user_fit = 50.0
    user_fit_reasons: list[str] = []
    if len(users) >= 80: user_fit += 25; user_fit_reasons.append("The target-user definition is detailed enough for focused validation.")
    elif len(users) >= 40: user_fit += 15; user_fit_reasons.append("The target-user definition is reasonably specific.")
    else: user_fit -= 10; user_fit_reasons.append("Identify who has the problem and why they would use the product.")
    if any(word in tokens for word in {"problem", "pain", "need", "challenge", "save", "reduce", "improve"}): user_fit += 8; user_fit_reasons.append("The description contains a user problem or desired outcome.")
    else: user_fit_reasons.append("A concrete user problem or measurable outcome is not yet explicit.")
    user_fit = clamp(user_fit)

    parameters = [_parameter(name, text, tokens, tech, description, users, risk_flags) for name in PARAMETER_NAMES]
    parameter_average = sum(p.score for p in parameters) / len(parameters)
    overall = clamp(feasibility * 0.24 + risk_score * 0.18 + originality * 0.16 + scope * 0.14 + user_fit * 0.12 + parameter_average * 0.16)
    confidence = clamp(45 + min(25, len(description) // 50) + min(15, len(users) // 20) + min(15, len(tech) * 3))

    if overall >= 80: verdict = "Strong starting point"
    elif overall >= 65: verdict = "Promising, but needs refinement"
    elif overall >= 50: verdict = "Needs significant refinement"
    else: verdict = "High-risk concept that needs redesign"

    base_recommendations = generate_recommendations(text=text, technologies=tech, feasibility=feasibility, originality=originality, scope=scope, user_fit=user_fit, risk_points=risk_points, risk_flags=risk_flags, unknown_tech=unknown_tech)
    analysis_snapshot = {"overall_score": overall, "verdict": verdict, "confidence": confidence, "feasibility": feasibility, "technical_risk": risk_score, "originality": originality, "scope_clarity": scope, "user_fit": user_fit, "parameters": [p.model_dump() for p in parameters], "risk_flags": [flag.model_dump() for flag in risk_flags]}
    enhanced_recommendations, recommendation_source = enhance_recommendations(project={"title": title, "description": description, "target_users": users, "technologies": sorted(tech)}, analysis=analysis_snapshot, base_recommendations=base_recommendations)

    return AnalysisResponse(
        project_title=title, overall_score=overall, verdict=verdict, confidence=confidence,
        feasibility=DimensionScore(score=feasibility, level=score_level(feasibility), reasons=feasibility_reasons),
        technical_risk=DimensionScore(score=risk_score, level=risk_level(risk_score), reasons=risk_reasons),
        originality=DimensionScore(score=originality, level=score_level(originality), reasons=originality_reasons),
        scope_clarity=DimensionScore(score=scope, level=score_level(scope), reasons=scope_reasons),
        user_fit=DimensionScore(score=user_fit, level=score_level(user_fit), reasons=user_fit_reasons),
        parameters=parameters, risk_flags=risk_flags, recommendations=enhanced_recommendations, recommendation_source=recommendation_source,
    )
