import os
import random
import requests
import streamlit as st

API_URL = os.getenv("PROJECTXRAY_API_URL", "https://projectxray-api.onrender.com").rstrip("/")
LOGIN_URL = f"{API_URL}/api/v1/auth/login"
REGISTER_URL = f"{API_URL}/api/v1/auth/register"
ANALYZE_URL = f"{API_URL}/api/v1/analyze"
RECOMMEND_URL = f"{API_URL}/api/v1/recommend"
HISTORY_URL = f"{API_URL}/api/v1/projects"

st.set_page_config(page_title="ProjectX-Ray", page_icon="🔎", layout="wide")

EXAMPLES = [
    {"title":"Campus Lost & Found","description":"A web platform where students report lost items, upload photos, search matching reports, and contact the owner through a controlled request flow.","users":"College students and campus administrators","tech":"Python, FastAPI, Streamlit, SQLite"},
    {"title":"Study Planner for Final-Year Students","description":"A planner that converts subjects, deadlines, available study hours, and weak topics into a realistic weekly study schedule with progress tracking.","users":"Final-year engineering students","tech":"Python, FastAPI, Streamlit, SQLite"},
    {"title":"Local Clinic Appointment System","description":"A booking system where patients view available slots, request appointments, and receive confirmation while clinic staff manage schedules and cancellations.","users":"Patients, doctors, and clinic staff","tech":"Python, FastAPI, PostgreSQL, Docker"},
]

st.markdown("""<style>
.block-container{max-width:1180px;padding-top:1.8rem;padding-bottom:3rem}.hero{padding:1.7rem;border:1px solid #30343b;border-radius:20px;background:linear-gradient(135deg,#10131a,#191d28)}.hero h1{margin:0;font-size:2.65rem}.hero p{color:#aab1bf;font-size:1.08rem}.pill{display:inline-block;padding:.3rem .65rem;border-radius:999px;background:#242936;color:#d8deea;font-size:.82rem;margin:.3rem}.rec{padding:.9rem 1rem;border-left:4px solid #6c8cff;background:#171a22;border-radius:8px;margin:.55rem 0}.risk{padding:.75rem 1rem;border-left:4px solid #ff6b6b;background:#24171a;border-radius:8px;margin:.45rem 0}.login-card{max-width:520px;margin:7vh auto;padding:2.2rem;border:1px solid #30343b;border-radius:22px;background:linear-gradient(135deg,#10131a,#191d28)}
</style>""",unsafe_allow_html=True)

for key, default in [("authenticated",False),("user_email",""),("analysis",None),("agent_messages",[])]:
    if key not in st.session_state: st.session_state[key]=default
if "project_data" not in st.session_state: st.session_state.project_data={"title":"","description":"","users":"","tech":""}

# Authentication
if not st.session_state.authenticated:
    st.markdown("<div class='login-card'>",unsafe_allow_html=True)
    st.markdown("# 🔎 ProjectX-Ray")
    st.caption("Create an account or sign in to your personal project workspace.")
    login_tab, register_tab = st.tabs(["🔐 Sign in","🆕 Create account"])
    with login_tab:
        with st.form("login"):
            email=st.text_input("Email",key="login_email")
            password=st.text_input("Password",type="password",key="login_password")
            submit=st.form_submit_button("Sign in",type="primary",use_container_width=True)
        if submit:
            try:
                r=requests.post(LOGIN_URL,json={"email":email,"password":password},timeout=15); r.raise_for_status(); data=r.json()
                if data.get("authenticated"):
                    st.session_state.authenticated=True; st.session_state.user_email=data["user"]; st.rerun()
                st.error(data.get("message","Invalid credentials."))
            except Exception as exc: st.error(f"Login service unavailable: {exc}")
    with register_tab:
        with st.form("register"):
            new_email=st.text_input("Email",key="reg_email")
            new_password=st.text_input("Password",type="password",key="reg_password")
            confirm=st.text_input("Confirm password",type="password")
            create=st.form_submit_button("Create account",type="primary",use_container_width=True)
        if create:
            if new_password!=confirm: st.error("Passwords do not match.")
            else:
                try:
                    r=requests.post(REGISTER_URL,json={"email":new_email,"password":new_password},timeout=15); r.raise_for_status(); data=r.json()
                    if data.get("authenticated"):
                        st.session_state.authenticated=True; st.session_state.user_email=data["user"]; st.success("Account created!"); st.rerun()
                    else: st.error(data.get("message","Could not create account."))
                except Exception as exc: st.error(f"Registration service unavailable: {exc}")
    st.info("Demo account: demo@projectxray.app / projectxray123")
    st.markdown("</div>",unsafe_allow_html=True)
    st.stop()

st.markdown("""<div class='hero'><h1>🔎 ProjectX-Ray</h1><p>Stress-test your project before you build it.</p><span class='pill'>Personal workspace</span><span class='pill'>Explainable scoring</span><span class='pill'>Built-in recommendation agent</span></div>""",unsafe_allow_html=True)

with st.sidebar:
    st.header("👤 My account")
    st.write(st.session_state.user_email)
    if st.button("📚 My project history",use_container_width=True): st.session_state.show_history=True
    if st.button("🚪 Logout",use_container_width=True):
        for key in ["authenticated","user_email","analysis","agent_messages","show_history"]: st.session_state.pop(key,None)
        st.rerun()
    st.divider()
    if st.button("✨ Load example",use_container_width=True): st.session_state.project_data=random.choice(EXAMPLES); st.session_state.analysis=None; st.rerun()
    if st.button("🧹 New project",use_container_width=True): st.session_state.project_data={"title":"","description":"","users":"","tech":""}; st.session_state.analysis=None; st.rerun()

if st.session_state.get("show_history"):
    st.subheader("📚 My Project History")
    try:
        r=requests.get(f"{HISTORY_URL}/{st.session_state.user_email}",timeout=15); r.raise_for_status(); history=r.json()
        if not history: st.info("No saved projects yet. Submit your first project below.")
        for item in history:
            with st.expander(f"{item['title']} · Score {item['analysis']['overall_score']}/100 · {item['created_at']}"):
                st.write(item["description"]); st.caption(f"Users: {item['target_users']} · Tech: {', '.join(item['technologies']) or 'Not specified'}")
                st.metric("Overall score",item["analysis"]["overall_score"])
                if st.button("Open this project",key=f"open_{item['id']}"):
                    st.session_state.project_data={"title":item["title"],"description":item["description"],"users":item["target_users"],"tech":", ".join(item["technologies"])}
                    st.session_state.analysis=item["analysis"]; st.session_state.show_history=False; st.rerun()
    except Exception as exc: st.error(f"Could not load project history: {exc}")
    st.divider()

st.subheader("1. Define your project")
with st.form("project_form"):
    title=st.text_input("Project title",value=st.session_state.project_data["title"])
    description=st.text_area("What are you building?",value=st.session_state.project_data["description"],height=150)
    c1,c2=st.columns(2)
    with c1: users=st.text_input("Who will use it?",value=st.session_state.project_data["users"])
    with c2: tech=st.text_input("Technologies",value=st.session_state.project_data["tech"])
    submitted=st.form_submit_button("🚀 Stress-test my project",type="primary",use_container_width=True)

if submitted:
    if len(title.strip())<3 or len(description.strip())<20 or len(users.strip())<3:
        st.error("Enter a title (3+ chars), description (20+ chars), and target users.")
    else:
        st.session_state.project_data={"title":title.strip(),"description":description.strip(),"users":users.strip(),"tech":tech.strip()}
        payload={"title":title.strip(),"description":description.strip(),"target_users":users.strip(),"technologies":[x.strip() for x in tech.split(",") if x.strip()]}
        try:
            r=requests.post(f"{ANALYZE_URL}?email={st.session_state.user_email}",json=payload,timeout=35); r.raise_for_status(); st.session_state.analysis=r.json(); st.session_state.agent_messages=[]; st.success("Analysis complete and saved to your workspace.")
        except Exception as exc: st.error(f"Analysis failed: {exc}")

result=st.session_state.analysis
if result:
    st.divider(); st.subheader(f"2. ProjectX-Ray report — {result['project_title']}")
    cols=st.columns(6)
    for col,(label,key) in zip(cols,[("Overall","overall_score"),("Feasibility","feasibility"),("Technical risk","technical_risk"),("Originality","originality"),("Scope","scope_clarity"),("User fit","user_fit")]): col.metric(label,result[key] if isinstance(result[key],int) else result[key]["score"])
    st.info(f"**Verdict:** {result['verdict']} · **Confidence:** {result['confidence']}/100")
    left,right=st.columns(2)
    with left:
        st.markdown("### 🎯 Why these scores?")
        for key,label in [("feasibility","Feasibility"),("technical_risk","Technical risk"),("originality","Originality"),("scope_clarity","Scope clarity"),("user_fit","User fit")]:
            item=result[key]; st.markdown(f"**{label}: {item['score']}/100 — {item['level']}**")
            for reason in item["reasons"]: st.markdown(f"- {reason}")
    with right:
        st.markdown("### 💡 Recommendations")
        for i,rec in enumerate(result["recommendations"],1): st.markdown(f"<div class='rec'><b>{i}.</b> {rec}</div>",unsafe_allow_html=True)
        for flag in result["risk_flags"]: st.markdown(f"<div class='risk'><b>{flag['severity'].upper()}</b> · {flag['category']}<br>{flag['message']}</div>",unsafe_allow_html=True)
    st.divider(); st.subheader("3. 🤖 Ask the recommendation agent")
    for m in st.session_state.agent_messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            for step in m.get("steps",[]): st.markdown(f"- {step}")
    q=st.chat_input("What should I build first? How can I improve originality?")
    if q:
        st.session_state.agent_messages.append({"role":"user","content":q})
        project={"title":st.session_state.project_data["title"],"description":st.session_state.project_data["description"],"target_users":st.session_state.project_data["users"],"technologies":[x.strip() for x in st.session_state.project_data["tech"].split(",") if x.strip()]}
        try:
            r=requests.post(RECOMMEND_URL,json={"project":project,"analysis":result,"question":q},timeout=35); r.raise_for_status(); data=r.json(); st.session_state.agent_messages.append({"role":"assistant","content":data["answer"],"steps":data.get("next_steps",[])}); st.rerun()
        except Exception as exc: st.error(f"Agent unavailable: {exc}")
else:
    st.info("Submit a project to generate your explainable report and save it to your personal history.")
