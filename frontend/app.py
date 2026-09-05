import os
import random

import requests
import streamlit as st

API_URL = os.getenv("PROJECTXRAY_API_URL", "https://projectxray-api.onrender.com").rstrip("/")
ANALYZE_URL = f"{API_URL}/api/v1/analyze"
HEALTH_URL = f"{API_URL}/health"

st.set_page_config(page_title="ProjectX-Ray", page_icon="🔎", layout="wide")

st.markdown(
    """
    <style>
    .block-container {max-width: 1180px; padding-top: 2rem;}
    .hero {padding: 1.4rem 1.6rem; border: 1px solid #30343b; border-radius: 18px; background: linear-gradient(135deg,#11131a,#181b24);}
    .hero h1 {margin: 0; font-size: 2.5rem;}
    .hero p {margin: .45rem 0 0; color: #aab1bf; font-size: 1.05rem;}
    .card {padding: 1rem 1.1rem; border: 1px solid #30343b; border-radius: 14px; background: #11131a;}
    .rec {padding: .85rem 1rem; border-left: 4px solid #6c8cff; background: #171a22; border-radius: 8px; margin: .55rem 0;}
    .risk {padding: .75rem 1rem; border-left: 4px solid #ff6b6b; background: #24171a; border-radius: 8px; margin: .45rem 0;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>🔎 ProjectX-Ray</h1>
      <p>Build your own project idea, then stress-test it before you spend your time building it.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

with st.sidebar:
    st.header("Your project")
    st.caption("Everything below is user-defined. The app does not require the demo project.")
    st.caption(f"Backend: {API_URL}")
    if st.button("Check backend", use_container_width=True):
        try:
            health = requests.get(HEALTH_URL, timeout=10)
            health.raise_for_status()
            st.success("Backend is online")
        except requests.RequestException as exc:
            st.error("Backend is not reachable")
            st.code(str(exc))

# Keep examples separate from the actual user workflow.
EXAMPLES = [
    {
        "title": "Campus Lost & Found",
        "description": "A web platform where students report lost items, upload photos, search matching reports, and contact the owner through a controlled request flow.",
        "users": "College students and campus administrators",
        "tech": "Python, FastAPI, Streamlit, SQLite",
    },
    {
        "title": "Study Planner for Final-Year Students",
        "description": "A planner that converts subjects, deadlines, available study hours, and weak topics into a realistic weekly study schedule with progress tracking.",
        "users": "Final-year engineering students",
        "tech": "Python, FastAPI, Streamlit, SQLite",
    },
    {
        "title": "Local Clinic Appointment System",
        "description": "A booking system where patients view available slots, request appointments, and receive confirmation while clinic staff manage schedules and cancellations.",
        "users": "Patients, doctors, and clinic staff",
        "tech": "Python, FastAPI, PostgreSQL, Docker",
    },
]

if "project_data" not in st.session_state:
    st.session_state.project_data = {
        "title": "",
        "description": "",
        "users": "",
        "tech": "",
    }

if "analysis" not in st.session_state:
    st.session_state.analysis = None

controls = st.columns([1, 1, 1, 2])
with controls[0]:
    if st.button("✨ Example", use_container_width=True):
        st.session_state.project_data = random.choice(EXAMPLES).copy()
        st.session_state.analysis = None
        st.rerun()
with controls[1]:
    if st.button("🧹 Clear", use_container_width=True):
        st.session_state.project_data = {"title": "", "description": "", "users": "", "tech": ""}
        st.session_state.analysis = None
        st.rerun()
with controls[2]:
    if st.button("🔄 New idea", use_container_width=True):
        st.session_state.project_data = random.choice(EXAMPLES).copy()
        st.session_state.analysis = None
        st.rerun()

st.subheader("1. Define your own project")
st.caption("Enter any project you want. You control the idea, users, and technology stack.")

with st.form("project_form", clear_on_submit=False):
    title = st.text_input(
        "Project title",
        value=st.session_state.project_data["title"],
        placeholder="e.g. Smart Campus Lost & Found",
    )
    description = st.text_area(
        "What are you building?",
        value=st.session_state.project_data["description"],
        height=150,
        placeholder="Explain the problem, what the system does, and its main features...",
    )
    users = st.text_input(
        "Who will use it?",
        value=st.session_state.project_data["users"],
        placeholder="e.g. College students and campus staff",
    )
    tech = st.text_input(
        "Technologies (comma separated)",
        value=st.session_state.project_data["tech"],
        placeholder="e.g. Python, FastAPI, Streamlit, PostgreSQL",
    )
    submitted = st.form_submit_button("🚀 Stress-test my project", type="primary", use_container_width=True)

if submitted:
    st.session_state.project_data = {
        "title": title,
        "description": description,
        "users": users,
        "tech": tech,
    }

    errors = []
    if len(title.strip()) < 3:
        errors.append("Project title must contain at least 3 characters.")
    if len(description.strip()) < 20:
        errors.append("Project description must contain at least 20 characters.")
    if len(users.strip()) < 3:
        errors.append("Please specify who will use the project.")

    if errors:
        for error in errors:
            st.error(error)
        st.session_state.analysis = None
    else:
        payload = {
            "title": title.strip(),
            "description": description.strip(),
            "target_users": users.strip(),
            "technologies": [item.strip() for item in tech.split(",") if item.strip()],
        }
        with st.spinner("Stress-testing your project..."):
            try:
                response = requests.post(ANALYZE_URL, json=payload, timeout=30)
                if response.status_code >= 400:
                    try:
                        detail = response.json().get("detail", response.text)
                    except ValueError:
                        detail = response.text
                    raise RuntimeError(f"Backend returned HTTP {response.status_code}: {detail}")
                st.session_state.analysis = response.json()
                st.success("Analysis completed successfully.")
            except (requests.RequestException, RuntimeError, ValueError) as exc:
                st.session_state.analysis = None
                st.error("The project could not be submitted to the backend.")
                st.code(str(exc))
                st.info("Use the 'Check backend' button in the sidebar to verify the API connection.")

result = st.session_state.analysis

if result:
    st.divider()
    st.subheader(f"2. ProjectX-Ray report — {result['project_title']}")

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

    st.info(f"**Verdict:** {result['verdict']}  ·  **Confidence:** {result['confidence']}/100")

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
        st.markdown("### 💡 Recommendations")
        for index, recommendation in enumerate(result["recommendations"], start=1):
            st.markdown(f'<div class="rec"><b>{index}.</b> {recommendation}</div>', unsafe_allow_html=True)

        if result["risk_flags"]:
            st.markdown("### ⚠️ Risk flags")
            for flag in result["risk_flags"]:
                st.markdown(
                    f'<div class="risk"><b>{flag["severity"].upper()}</b> · {flag["category"]}<br>{flag["message"]}</div>',
                    unsafe_allow_html=True,
                )

    st.caption("This report is screening guidance based on the information you entered; it is not proof of project success.")
else:
    st.divider()
    st.subheader("2. Your result will appear here")
    st.write("Fill in your project and click **🚀 Stress-test my project**. The app will submit your actual inputs to the deployed FastAPI backend and return the analysis.")
