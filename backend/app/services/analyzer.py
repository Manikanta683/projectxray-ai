from ..schemas.project import AnalysisResponse, DimensionScore, ProjectIdeaRequest


HIGH_RISK_TERMS = {
    "real-time", "blockchain", "medical", "healthcare", "autonomous",
    "drone", "biometric", "payment", "financial", "face recognition",
    "iot", "quantum", "self-driving", "critical infrastructure",
}

COMMON_TECH = {
    "python", "fastapi", "flask", "django", "javascript", "typescript",
    "react", "node", "postgresql", "mysql", "mongodb", "docker",
    "streamlit", "scikit-learn", "pytorch", "tensorflow",
}


def level(score: int) -> str:
    if score >= 80:
        return "Low concern"
    if score >= 60:
        return "Moderate concern"
    if score >= 40:
        return "High concern"
    return "Critical concern"


def analyze_project(project: ProjectIdeaRequest) -> AnalysisResponse:
    text = f"{project.title} {project.description} {project.target_users}".lower()
    tech = {item.lower().strip() for item in project.technologies}

    feasibility = 70
    feasibility_reasons = []
    if len(project.description) >= 120:
        feasibility += 10
        feasibility_reasons.append("The idea has enough description to define an initial scope.")
    else:
        feasibility -= 10
        feasibility_reasons.append("The project description is short; the MVP scope should be clarified.")
    if tech:
        feasibility += 10
        feasibility_reasons.append("A technology stack has been identified.")
    else:
        feasibility -= 10
        feasibility_reasons.append("No technology stack was provided.")
    feasibility = max(0, min(100, feasibility))

    risk = 25
    risk_reasons = []
    matched_risks = [term for term in HIGH_RISK_TERMS if term in text]
    if matched_risks:
        risk += min(45, len(matched_risks) * 10)
        risk_reasons.append("Higher-risk requirements detected: " + ", ".join(matched_risks[:4]) + ".")
    else:
        risk_reasons.append("No major high-risk requirement keywords were detected.")
    unknown_tech = sorted(tech - COMMON_TECH)
    if unknown_tech:
        risk += min(20, len(unknown_tech) * 5)
        risk_reasons.append("Some technologies need validation before implementation: " + ", ".join(unknown_tech[:4]) + ".")
    risk = max(0, min(100, risk))
    risk_score = 100 - risk

    originality = 55
    originality_reasons = []
    generic_terms = {"chatbot", "e-commerce", "social media", "attendance", "todo", "portfolio"}
    generic_matches = [term for term in generic_terms if term in text]
    if generic_matches:
        originality -= min(30, len(generic_matches) * 10)
        originality_reasons.append("The concept uses a common project category: " + ", ".join(generic_matches) + ".")
    else:
        originality += 10
        originality_reasons.append("The description does not strongly match the built-in generic project categories.")
    if len(project.target_users) >= 40:
        originality += 10
        originality_reasons.append("A specific user group is described, which can support differentiation.")
    originality = max(0, min(100, originality))

    overall = round((feasibility + risk_score + originality) / 3)
    if overall >= 80:
        verdict = "Strong starting point"
    elif overall >= 65:
        verdict = "Promising, but needs refinement"
    elif overall >= 50:
        verdict = "Needs significant refinement"
    else:
        verdict = "High-risk concept that needs redesign"

    recommendations = []
    if feasibility < 75:
        recommendations.append("Define a smaller MVP with one measurable outcome.")
    if risk >= 45:
        recommendations.append("Prototype the highest-risk technical requirement before building the full system.")
    if originality < 70:
        recommendations.append("Add a specific differentiator tied to a clearly defined user problem.")
    if not project.technologies:
        recommendations.append("Choose a practical initial technology stack and justify each major component.")
    recommendations.append("Validate the idea with target users before investing in advanced features.")

    return AnalysisResponse(
        project_title=project.title,
        overall_score=overall,
        verdict=verdict,
        feasibility=DimensionScore(score=feasibility, level=level(feasibility), reasons=feasibility_reasons),
        technical_risk=DimensionScore(score=risk_score, level=level(risk_score), reasons=risk_reasons),
        originality=DimensionScore(score=originality, level=level(originality), reasons=originality_reasons),
        recommendations=recommendations,
    )
