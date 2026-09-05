"""Built-in contextual recommendation enhancement.

No external model, API key, network call, or account setup is required.
"""


def enhance_recommendations(*, project: dict, analysis: dict, base_recommendations: list[str]) -> tuple[list[str], str]:
    recs = list(base_recommendations)
    score_pairs = [
        (analysis.get("scope_clarity", 100), "scope", "Put the first release behind one clear MVP outcome and explicitly move secondary features to a future phase."),
        (analysis.get("user_fit", 100), "users", "Validate the project with the primary user group and define one measurable improvement they should experience."),
        (analysis.get("originality", 100), "originality", "Strengthen differentiation by choosing one specific user segment, workflow, or measurable advantage that existing alternatives do not emphasize."),
        (analysis.get("feasibility", 100), "feasibility", "Build the riskiest end-to-end workflow as a thin prototype before implementing the full feature set."),
        (analysis.get("technical_risk", 100), "risk", "Test the highest-impact technical risk first and document the failure behavior before expanding the system."),
    ]
    for score, _, message in sorted(score_pairs, key=lambda item: item[0]):
        if score < 70 and message not in recs:
            recs.append(message)
    # Keep the strongest existing recommendations first, then contextual additions.
    return recs[:8], "Built-in recommendation engine"
