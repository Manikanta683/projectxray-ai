from ..schemas.project import RiskFlag


def generate_recommendations(
    *,
    text: str,
    technologies: set[str],
    feasibility: int,
    originality: int,
    scope: int,
    user_fit: int,
    risk_points: float,
    risk_flags: list[RiskFlag],
    unknown_tech: list[str],
) -> list[str]:
    """Generate recommendations from the actual weaknesses and requirements of a project."""
    recommendations: list[str] = []
    lower = text.lower()

    def add(message: str) -> None:
        if message not in recommendations:
            recommendations.append(message)

    # Recommendations specific to project-idea generation and mentoring systems.
    if any(term in lower for term in ("project idea", "project ideas", "idea generator", "generate project")) and any(term in lower for term in ("student", "college", "final-year", "final year")):
        add("Make personalization the core differentiator: collect each student's interests, skills, preferred domain, time available, and current experience before generating ideas.")
        add("Rank generated ideas against an explicit rubric such as skill match, feasibility, originality, implementation effort, and expected learning value instead of returning an unranked list.")
        add("Keep the mentor flow actionable: for every selected idea, produce an MVP boundary, recommended features, technology choices, development milestones, and the main risks to validate first.")
        add("Use a curated project knowledge base or tagged historical examples to reduce repetitive ideas and explain why a recommendation is suitable for the student.")

    # Recommendations tied directly to detected risk domains.
    if any(term in lower for term in ("medical", "healthcare", "clinical")):
        add("For a health-related product, define privacy, consent, safety, validation, and regulatory boundaries before implementation.")
    if any(term in lower for term in ("payment", "financial", "banking", "transaction")):
        add("For financial or payment workflows, design authentication, authorization, audit logs, idempotent transactions, fraud handling, and failure recovery before the UI.")
    if any(term in lower for term in ("biometric", "face recognition", "facial recognition")):
        add("For biometric features, validate accuracy and bias, obtain appropriate consent, minimize stored biometric data, and define a secure deletion policy.")
    if "real-time" in lower or "real time" in lower:
        add("For real-time requirements, define a latency target, concurrency target, failure behavior, and load-test the critical path before scaling the architecture.")
    if "blockchain" in lower:
        add("Use blockchain only where decentralization, shared trust, or verifiable ownership is genuinely required; compare it against a conventional database first.")
    if "drone" in lower or "autonomous" in lower or "self-driving" in lower:
        add("For autonomous or hardware-dependent features, start with simulation and a controlled prototype, then define fail-safe behavior and measurable safety tests.")
    if "iot" in lower:
        add("For IoT, validate device connectivity, offline behavior, firmware/version handling, telemetry, and secure device authentication with a small hardware pilot.")
    if any(term in lower for term in ("predict", "prediction", "detect", "classification", "machine learning", "model")):
        add("For predictive or detection features, define the target metric, collect representative data, establish a simple baseline, and test false positives and false negatives before choosing a complex model.")

    # Recommendations tied to stack choices.
    if any("tensorflow" in tech or "pytorch" in tech or "scikit-learn" in tech for tech in technologies):
        add("For the model component, separate data preparation, training, evaluation, and inference so the result can be reproduced and tested independently.")
    if "mongodb" in technologies and any(term in lower for term in ("transaction", "payment", "financial")):
        add("If the system handles critical financial transactions, verify that the chosen data model and consistency guarantees match the transaction requirements.")
    if "docker" in technologies:
        add("Containerize the MVP consistently and document environment variables, health checks, and the local development command.")
    if unknown_tech:
        add("Validate the least familiar technology first with a small proof of concept before making it a core dependency.")

    # Recommendations tied to score weaknesses.
    if scope < 70:
        add("Define one MVP outcome and remove features that do not directly prove that outcome.")
    if user_fit < 70:
        add("Specify one primary user segment, the problem they currently face, and a measurable improvement your product should deliver.")
    if originality < 70:
        add("Differentiate the concept with a specific user segment, workflow, proprietary/curated data source, or measurable advantage rather than adding features randomly.")
    if feasibility < 70:
        add("Build a thin vertical prototype of the riskiest end-to-end workflow before committing to the complete feature set.")
    if risk_points >= 35:
        add("Rank the detected risks by impact and uncertainty, then test the highest-impact assumption first with a small prototype.")
    if not technologies:
        add("Choose a minimal, practical technology stack and explain why each major component is needed.")

    # Always leave the user with a concrete validation action, but keep it contextual.
    if any(term in lower for term in ("student", "college", "campus", "education")):
        add("Pilot with a small group of real students and measure adoption, task completion, and whether the product saves meaningful time.")
    elif any(term in lower for term in ("business", "customer", "seller", "shop", "company")):
        add("Run a small pilot with representative users and measure the business outcome the product is supposed to improve.")
    else:
        add("Validate the core assumption with representative target users before expanding the feature set.")

    return recommendations[:8]
