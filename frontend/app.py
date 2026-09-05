import os
import random

import requests
import streamlit as st

API_URL = os.getenv("PROJECTXRAY_API_URL", "https://projectxray-api.onrender.com").rstrip("/")
ANALYZE_URL = f"{API_URL}/api/v1/analyze"
RECOMMEND_URL = f"{API_URL}/api/v1/recommend"
HEALTH_URL = f"{API_URL}/health"

st.set_page_config(page_title="ProjectX-Ray", page_icon="🔎", layout="wide", initial_sidebar_state="expanded")

EXAMPLES = [
    {"title": "Campus Lost & Found", "description": "A web platform where students report lost items, upload photos, search matching reports, and contact the owner through a controlled request flow.", "users": "College students and campus administrators", "tech": "Python, FastAPI, Streamlit, SQLite"},
    {"title": "Study Planner for Final-Year Students", "description": "A planner that converts subjects, deadlines, available study hours, and weak topics into a realistic weekly study schedule with progress tracking.", "users": "Final-year engineering students", "tech": "Python, FastAPI, Streamlit, SQLite"},
    {"title": "Local Clinic Appointment System", "description": "A booking system where patients view available slots, request appointments, and receive confirmation while clinic staff manage schedules and cancellations.", "users": "Patients, doctors, and clinic staff", "tech": "Python, FastAPI, PostgreSQL, Docker"},
]

st.markdown("""
<style>
.block-container {max-width: 1180px; padding-top: 1.8rem; padding-bottom: 3rem;}
.hero {padding: 1.7rem 1.8rem; border: 1px solid #30343b; border-radius: 20px; background: linear-gradient(135deg,#10131a,#191d28);}
.hero h1 {margin: 0; font-size: 2.65rem; letter-spacing: -.04em;}
.hero p {margin: .55rem 0 0; color: #aab1bf; font-size: 1.08rem;}
.pill {display:inline-block; padding:.3rem .65rem; border-radius:999px; background:#242936; color:#d8deea; font-size:.82rem; margin:.3rem .25rem 0 0;}
.rec {padding: .9rem 1rem; border-left: 4px solid #6c8cff; background: #171a22; border-radius: 8px; margin: .55rem 0;}
.risk {padding: .75rem 1rem; border-left: 4px solid #ff6b6b; background: #24171a; border-radius: 8px; margin: .45rem 0;}
.agent {padding: 1rem 1.1rem; border: 1px solid #30343b; background: #141720; border-radius: 12px; margin: .5rem 0;}
.source {padding:.65rem .85rem; border:1px solid #30343b; border-radius:10px; background:#141720; margin-bottom:.8rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🔎 ProjectX-Ray</h1>
  <p>Define your own project. Stress-test the idea. Get practical, personalized recommendations before you build.</p>
  <span class="pill">User-defined input</span><span class="pill">Explainable scoring</span><span class="pill">Live recommendation agent</span>
</div>
""", unsafe_allow_html=True)

if "project_data" not in st.session_state:
    st.session_state.project_data = {"title": "", "description": "", "users": "", "tech": ""}
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = []

with st.sidebar:
    st.header("⚙️ Project controls")
    st.caption("This is a real submission workflow — examples are optional.")
    if st.button("✨ Load example", use_container_width=True):
        st.session_state.project_data = random.choice(EXAMPLES).copy()
        st.session_state.analysis = None
        st.session_state.agent_messages = []
        st.rerun()
    if st.button("🧹 Clear project", use_container_width=True):
        st.session_state.project_data = {"title": "", "description": "", "users": "", "tech": ""}
        st.session_state.analysis = None
        st.session_state.agent_messages = []
        st.rerun()
    st.divider()
    st.caption(f"API: {API_URL}")
    if st.button("Check backend", use_container_width=True):
        try:
            health = requests.get(HEALTH_URL, timeout=10)
            health.raise_for_status()
            st.success("Backend is online")
        except requests.RequestException as exc:
            st.error("Backend is not reachable")
            st.code(str(exc))

st.subheader("1. Define your project")
st.caption("You control the idea. ProjectX-Ray evaluates the exact information you submit.")

with st.form("project_form", clear_on_submit=False):
    title = st.text_input("Project title", value=st.session_state.project_data["title"], placeholder="e.g. Smart Campus Lost & Found")
    description = st.text_area("What are you building?", value=st.session_state.project_data["description"], height=160, placeholder="Describe the problem, who it helps, what the system does, and the main features you want in the first version...")
    c1, c2 = st.columns(2)
    with c1:
        users = st.text_input("Who will use it?", value=st.session_state.project_data["users"], placeholder="e.g. College students and campus staff")
    with c2:
        tech = st.text_input("Technologies", value=st.session_state.project_data["tech"], placeholder="e.g. Python, FastAPI, Streamlit, PostgreSQL")
    submitted = st.form_submit_button("🚀 Stress-test my project", type="primary", use_container_width=True)

if submitted:
    st.session_state.project_data = {"title": title, "description": description, "users": users, "tech": tech}
    st.session_state.agent_messages = []
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
        payload = {"title": title.strip(), "description": description.strip(), "target_users": users.strip(), "technologies": [item.strip() for item in tech.split(",") if item.strip()]}
        with st.spinner("Stress-testing your project and preparing recommendations..."):
            try:
                response = requests.post(ANALYZE_URL, json=payload, timeout=35)
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
                st.info("Use 'Check backend' in the sidebar to verify the API connection.")

result = st.session_state.analysis
if result:
    st.divider()
    st.subheader(f"2. ProjectX-Ray report — {result['project_title']}")
    source = result.get("recommendation_source", "Rule-based fallback")
    source_label = "✨ Enhanced recommendations" if source != "Rule-based fallback" else "🧩 Deterministic recommendations"
    st.markdown(f'<div class="source"><b>{source_label}</b> · Recommendation engine: {source}</div>', unsafe_allow_html=True)

    cols = st.columns(6)
    for col, (label, value) in zip(cols, [("Overall", result["overall_score"]), ("Feasibility", result["feasibility"]["score"]), ("Technical risk", result["technical_risk"]["score"]), ("Originality", result["originality"]["score"]), ("Scope", result["scope_clarity"]["score"]), ("User fit", result["user_fit"]["score"])]):
        col.metric(label, value)

    st.info(f"**Verdict:** {result['verdict']}  ·  **Confidence:** {result['confidence']}/100")
    left, right = st.columns(2)
    with left:
        st.markdown("### 🎯 Why these scores?")
        for key, label in [("feasibility", "Feasibility"), ("technical_risk", "Technical risk"), ("originality", "Originality"), ("scope_clarity", "Scope clarity"), ("user_fit", "User fit")]:
            item = result[key]
            st.markdown(f"**{label}: {item['score']}/100 — {item['level']}**")
            for reason in item["reasons"]:
                st.markdown(f"- {reason}")
    with right:
        st.markdown("### 💡 Personalized recommendations")
        for index, recommendation in enumerate(result["recommendations"], start=1):
            st.markdown(f'<div class="rec"><b>{index}.</b> {recommendation}</div>', unsafe_allow_html=True)
        if result["risk_flags"]:
            st.markdown("### ⚠️ Risk flags")
            for flag in result["risk_flags"]:
                st.markdown(f'<div class="risk"><b>{flag["severity"].upper()}</b> · {flag["category"]}<br>{flag["message"]}</div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("3. 🤖 Ask the live recommendation agent")
    st.caption("Ask follow-up questions about your submitted project. The agent receives your project and ProjectX-Ray report through the FastAPI API.")

    for message in st.session_state.agent_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("steps"):
                st.markdown("**Suggested next steps:**")
                for step in message["steps"]:
                    st.markdown(f"- {step}")

    question = st.chat_input("e.g. What should I build first for the MVP?")
    if question:
        st.session_state.agent_messages.append({"role": "user", "content": question})
        project_payload = {
            "title": st.session_state.project_data["title"].strip(),
            "description": st.session_state.project_data["description"].strip(),
            "target_users": st.session_state.project_data["users"].strip(),
            "technologies": [item.strip() for item in st.session_state.project_data["tech"].split(",") if item.strip()],
        }
        agent_payload = {"project": project_payload, "analysis": result, "question": question.strip()}
        try:
            with st.spinner("Recommendation agent is thinking..."):
                response = requests.post(RECOMMEND_URL, json=agent_payload, timeout=35)
                if response.status_code >= 400:
                    try:
                        detail = response.json().get("detail", response.text)
                    except ValueError:
                        detail = response.text
                    raise RuntimeError(f"Agent API returned HTTP {response.status_code}: {detail}")
                data = response.json()
            st.session_state.agent_messages.append({"role": "assistant", "content": data["answer"], "steps": data.get("next_steps", []), "source": data.get("source")})
            st.rerun()
        except (requests.RequestException, RuntimeError, ValueError, KeyError) as exc:
            st.session_state.agent_messages.append({"role": "assistant", "content": f"I couldn't reach the recommendation agent right now. The built-in recommendations are still available above.\n\nTechnical detail: `{exc}`"})
            st.rerun()

    st.caption("The external model does not control the explainable scores. It only provides contextual recommendation text; without an API key, the agent safely uses a built-in fallback.")
else:
    st.divider()
    st.subheader("2. Your result will appear here")
    st.write("Submit your own project above. ProjectX-Ray will send your exact inputs to the deployed FastAPI backend and return scores, reasons, risks, and recommendations.")
