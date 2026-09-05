"""Conversational recommendation agent for ProjectX-Ray."""

import json
import os
from typing import Any

import requests


def _build_prompt(project: dict[str, Any], analysis: dict[str, Any], question: str) -> str:
    return f"""You are ProjectX-Ray's senior project recommendation agent.

Answer the user's question using ONLY the supplied project and analysis context. Be practical, specific, and concise. The user is typically a final-year engineering student, so prioritize achievable implementation steps.

Project:
{json.dumps(project, ensure_ascii=False)}

ProjectX-Ray analysis:
{json.dumps(analysis, ensure_ascii=False)}

User question:
{question}

Rules:
- Do not change or contradict the supplied scores or risk flags.
- Do not invent datasets, users, regulations, integrations, or performance numbers.
- Recommend a small MVP first and clearly separate optional future improvements.
- Mention concrete technologies only when supported by the project context.
- If the user asks what to build next, give an ordered plan.
- Return ONLY valid JSON in this shape:
{{"answer":"...","next_steps":["...","..."]}}
"""


def _parse(data: dict[str, Any]) -> tuple[str, list[str]]:
    answer = str(data.get("answer", "")).strip()
    steps = data.get("next_steps", [])
    if not isinstance(steps, list):
        steps = []
    steps = [str(item).strip() for item in steps if str(item).strip()][:6]
    if not answer:
        raise ValueError("Agent returned an empty answer")
    return answer, steps


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
    raise ValueError("Agent did not return valid JSON")


def _gemini(prompt: str, key: str, model: str) -> tuple[str, list[str]]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 900,
            "responseMimeType": "application/json",
        },
    }
    response = requests.post(url, headers={"x-goog-api-key": key}, json=payload, timeout=25)
    response.raise_for_status()
    data = response.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    return _parse(_extract_json(text))


def _openai(prompt: str, key: str, model: str) -> tuple[str, list[str]]:
    url = "https://api.openai.com/v1/responses"
    payload = {"model": model, "input": prompt, "max_output_tokens": 900}
    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json=payload,
        timeout=25,
    )
    response.raise_for_status()
    data = response.json()
    text = data.get("output_text", "")
    if not text:
        for item in data.get("output", []):
            for content in item.get("content", []):
                if content.get("type") in {"output_text", "text"}:
                    text += content.get("text", "")
    return _parse(_extract_json(text))


def ask_agent(*, project: dict[str, Any], analysis: dict[str, Any], question: str) -> tuple[str, list[str], str]:
    provider = os.getenv("RECOMMENDATION_PROVIDER", "auto").strip().lower()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    prompt = _build_prompt(project, analysis, question)

    attempts = []
    if provider in {"auto", "gemini", "google"} and gemini_key:
        attempts.append(("Google Gemini", gemini_key, os.getenv("GEMINI_MODEL", "gemini-3.7-flash")))
    if provider in {"auto", "openai"} and openai_key:
        attempts.append(("OpenAI", openai_key, os.getenv("OPENAI_MODEL", "gpt-5-mini")))

    for name, key, model in attempts:
        try:
            if name == "Google Gemini":
                answer, steps = _gemini(prompt, key, model)
            else:
                answer, steps = _openai(prompt, key, model)
            return answer, steps, name
        except (requests.RequestException, KeyError, ValueError, json.JSONDecodeError):
            continue

    # Safe local fallback keeps the live demo usable when no external key is configured.
    recs = analysis.get("recommendations", [])
    answer = "Start with the highest-impact recommendation from the ProjectX-Ray report, keep the first version small, and validate the core workflow before adding advanced features."
    if question.lower().strip() in {"what should i build first?", "what should i do first?", "where should i start?"} and recs:
        answer = recs[0]
    steps = [str(item) for item in recs[:4]]
    return answer, steps, "Rule-based fallback"
