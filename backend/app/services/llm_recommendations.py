"""Optional LLM-powered recommendation enhancement.

The deterministic analyzer remains the source of scores and risk flags. This module
only enriches the recommendation text when a server-side Gemini or OpenAI key is
configured in the deployment environment.
"""

import json
import os
from typing import Any

import requests


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
    raise ValueError("LLM did not return valid JSON")


def _prompt(project: dict[str, Any], analysis: dict[str, Any], base_recommendations: list[str]) -> str:
    return f"""You are a senior engineering project mentor.

Improve the recommendations for this student project. Do not change the supplied scores, verdict, risk flags, or facts. Make recommendations specific to the actual project instead of generic advice.

Project:
{json.dumps(project, ensure_ascii=False)}

Deterministic analysis:
{json.dumps(analysis, ensure_ascii=False)}

Existing recommendations:
{json.dumps(base_recommendations, ensure_ascii=False)}

Return ONLY valid JSON with this shape:
{{"recommendations": ["..."]}}

Rules:
- Return 5 to 8 concise recommendations.
- Prioritize the highest-impact improvements first.
- Include an MVP boundary, implementation priorities, validation/testing, and the most relevant risks when applicable.
- Mention concrete technologies or architecture choices only when justified by the supplied project.
- For student projects, keep the plan achievable for a final-year project.
- Never invent users, datasets, regulations, integrations, or performance numbers.
- Do not repeat the project description.
"""


def _gemini(prompt: str, api_key: str, model: str) -> list[str]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.35,
            "maxOutputTokens": 900,
            "responseMimeType": "application/json",
        },
    }
    response = requests.post(url, headers={"x-goog-api-key": api_key}, json=payload, timeout=20)
    response.raise_for_status()
    data = response.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    return _parse_recommendations(_extract_json(text))


def _openai(prompt: str, api_key: str, model: str) -> list[str]:
    url = "https://api.openai.com/v1/responses"
    payload = {
        "model": model,
        "input": prompt,
        "temperature": 0.35,
        "max_output_tokens": 900,
    }
    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    text = data.get("output_text", "")
    if not text:
        for item in data.get("output", []):
            for content in item.get("content", []):
                if content.get("type") in {"output_text", "text"}:
                    text += content.get("text", "")
    return _parse_recommendations(_extract_json(text))


def _parse_recommendations(data: dict[str, Any]) -> list[str]:
    items = data.get("recommendations", [])
    if not isinstance(items, list):
        return []
    return [str(item).strip() for item in items if str(item).strip()][:8]


def enhance_recommendations(
    *,
    project: dict[str, Any],
    analysis: dict[str, Any],
    base_recommendations: list[str],
) -> tuple[list[str], str]:
    """Return enhanced recommendations and the provider used.

    If no key is configured, or an LLM call fails, the deterministic recommendations
    are returned so the product never becomes dependent on an external model.
    """
    provider = os.getenv("RECOMMENDATION_PROVIDER", "auto").strip().lower()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()

    prompt = _prompt(project, analysis, base_recommendations)

    attempts: list[tuple[str, str, str]] = []
    if provider in {"auto", "gemini", "google"} and gemini_key:
        attempts.append(("Google Gemini", gemini_key, os.getenv("GEMINI_MODEL", "gemini-3.7-flash")))
    if provider in {"auto", "openai"} and openai_key:
        attempts.append(("OpenAI", openai_key, os.getenv("OPENAI_MODEL", "gpt-5-mini")))

    for name, key, model in attempts:
        try:
            if name == "Google Gemini":
                recommendations = _gemini(prompt, key, model)
            else:
                recommendations = _openai(prompt, key, model)
            if recommendations:
                return recommendations, name
        except (requests.RequestException, KeyError, ValueError, json.JSONDecodeError):
            continue

    return base_recommendations, "Rule-based fallback"
