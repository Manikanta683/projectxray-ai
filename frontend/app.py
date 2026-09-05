import os

import requests
import streamlit as st

API_URL = os.getenv("PROJECTXRAY_API_URL", "http://127.0.0.1:8000").rstrip("/")
ANALYZE_URL = f"{API_URL}/api/v1/analyze"

DEMO_TITLE = "AI Project Idea Generator & Mentor for Final-Year Projects"
DEMO_DESCRIPTION = (
    "Build an AI-powered platform that helps final-year students generate project ideas "
    "based on their interests and skills and provides guidance on features, technologies, "
    "development steps, and improvements to turn the idea into a practical project."
)
DEMO_USERS = "Final-year engineering and college students selecting a practical project"
DEMO_TECH = "Python, FastAPI, Streamlit"

st.set_page_config(page_title="ProjectX-Ray", page_icon="🔎", layout="wide")

st.markdown(
    """
    <style>
    .block-container {max-width: 1200px; padding-top: 2rem;}
    .hero {padding: 1.2rem 1.4rem; border: 1px solid #dfe5ee; border-radius: 14px; background: #f8fafc;}
    .hero h1 {margin: 0; font-size: 2.1rem;}
    .hero p {margin: .35rem 0 0; color: #5b6472;}
    .rec {padding: .85rem 1rem; border-left: 4px solid #3b82f6; background: #f8fafc; border-radius: 8px; margin: .55rem 0;}
    .risk {padding: .75rem 1rem; border-left: 4px solid #ef4444; background: #fff7f7; border-radius: 8px; margin: .45rem 0;}
    .small {color:#6b7280; font-size:.9rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="hero">
      <h1>🔎 ProjectX-Ray</h1>
      <p>Live project stress-testing: feasibility, technical risk, originality, scope, user fit and recommendations.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(f"Live analysis endpoint: {ANALYZE_URL}")

with st.sidebar:
    st.header("Demo controls")
    if st.button("Load screenshot project", use_container_width=True):
        st.session_state.title = DEMO_TITLE
        st.session_state.description = DEMO_DESCRIPTION
        st.session_state.users = DEMO_USERS
        st.session_state.tech = DEMO_TECH
        st.rerun()
    live = st.toggle("Live recommendations", value=True)
    st.markdown("The report refreshes whenever the project inputs are changed and the page reruns.")

st.subheader("Project idea")
title = st.text_input("Project title", value=st.session_state.get("title", DEMO_TITLE), key="title")
description = st.text_area(
    "What are you building?",
    value=st.session_state.get("description", DEMO_DESCRIPTION),
    height=150,
    key="description",
)
users = st.text_input(
    "Target users",
    value=st.session_state.get("users", DEMO_USERS),
    key="users",
)
tech = st.text_input(
    "Technologies (comma separated)",
    value=st.session_state.get("tech", DEMO_TECH),
    key="tech",
)

payload = {
    "title": title,
    "description": description,
    "target_users": users,
    "technologies": [item.strip() for item in tech.split(",") if item.strip()],
}

if not live:
    if st.button("Analyze project", type="primary"):
        st.session_state.run_analysis = True

should_analyze = live or st.session_state.get("run_analysis", False)

if not title.strip() or len(description.strip()) < 20 or not users.strip():
    st.info("Enter a title, at least 20 characters of description, and target users to start the live analysis.")
    st.stop()

if should_analyze:
    try:
        response = requests.post(ANALYZE_URL, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        st.session_state.run_analysis = False
    except requests.RequestException as exc:
        st.error("ProjectX-Ray backend is not reachable. Start FastAPI on port 8000, then refresh this page.")
        st.code(str(exc))
        st.stop()

    st.divider()
    st.subheader("Live ProjectX-Ray report")

    cols = st.columns(6)
    metrics = [
        ("Overall", result["overall_score"]),
        ("Feasibility", result["feasibility"]["score"]),
        ("Technical risk", result["technical_risk"]["score"]),
        ("Originality", result["originality"]["score"]),
        ("Scope", result["scope_clarity"]["score"]),
        ("User fit", result["user_fit"]["score"]),
    ]
    for col, (label, value) in zip(cols, metrics):
        col.metric(label, value)

    st.info(f"**Verdict:** {result['verdict']}  ·  **Analysis confidence:** {result['confidence']}/100")

    left, right = st.columns(2)
    with left:
        st.markdown("### 🎯 Why these scores?")
        for key, label in [
            ("feasibility", "Feasibility"),
            ("technical_risk", "Technical risk"),
            ("originality", "Originality"),
            ("scope_clarity", "Scope clarity"),
            ("user_fit", "User fit"),
        ]:
            item = result[key]
            st.markdown(f"**{label}: {item['score']}/100 — {item['level']}**")
            for reason in item["reasons"]:
                st.markdown(f"- {reason}")

    with right:
        st.markdown("### 💡 Live recommendations")
        if result["recommendations"]:
            for index, recommendation in enumerate(result["recommendations"], start=1):
                st.markdown(f'<div class="rec"><b>{index}.</b> {recommendation}</div>', unsafe_allow_html=True)
        else:
            st.success("No additional recommendations were generated.")

        if result["risk_flags"]:
            st.markdown("### ⚠️ Detected risk flags")
            for flag in result["risk_flags"]:
                st.markdown(
                    f'<div class="risk"><b>{flag["severity"].upper()}</b> · {flag["category"]}<br>{flag["message"]}</div>',
                    unsafe_allow_html=True,
                )

    st.caption("Recommendations are generated from the current project description, users and technology stack; they are screening guidance, not proof of project success.")
