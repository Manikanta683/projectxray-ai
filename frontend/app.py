import os
import random
import requests
import streamlit as st

API_URL = os.getenv("PROJECTXRAY_API_URL", "https://projectxray-api.onrender.com").rstrip("/")
LOGIN_URL=f"{API_URL}/api/v1/auth/login"; REGISTER_URL=f"{API_URL}/api/v1/auth/register"; ANALYZE_URL=f"{API_URL}/api/v1/analyze"; RECOMMEND_URL=f"{API_URL}/api/v1/recommend"; HISTORY_URL=f"{API_URL}/api/v1/projects"

st.set_page_config(page_title="ProjectX-Ray", page_icon="🔎", layout="wide")
EXAMPLES=[
 {"title":"Campus Lost & Found","description":"A web platform where students report lost items, upload photos, search matching reports, and contact the owner through a controlled request flow.","users":"College students and campus administrators","tech":"Python, FastAPI, Streamlit, SQLite"},
 {"title":"Study Planner","description":"A planner that converts subjects, deadlines, available study hours, and weak topics into a realistic weekly study schedule with progress tracking.","users":"Final-year engineering students","tech":"Python, FastAPI, Streamlit, SQLite"},
 {"title":"Clinic Appointment System","description":"A booking system where patients view available slots, request appointments, and receive confirmation while clinic staff manage schedules and cancellations.","users":"Patients, doctors, and clinic staff","tech":"Python, FastAPI, PostgreSQL, Docker"},
]
PARAMETER_ICONS={"Code Quality":"🟢","Security":"🔵","Efficiency":"🟣","Testing":"⚪","Accessibility":"⚪","Problem Statement Alignment":"🟢"}

st.markdown("""<style>
.block-container{max-width:1180px;padding-top:1.8rem}.hero{padding:1.7rem;border:1px solid #30343b;border-radius:20px;background:linear-gradient(135deg,#10131a,#191d28)}.hero h1{margin:0}.hero p{color:#aab1bf;font-size:1.05rem}.pill{display:inline-block;padding:.3rem .65rem;border-radius:999px;background:#242936;color:#d8deea;font-size:.82rem;margin:.3rem}.rec{padding:.9rem 1rem;border-left:4px solid #6c8cff;background:#171a22;border-radius:8px;margin:.55rem 0}.risk{padding:.75rem 1rem;border-left:4px solid #ff6b6b;background:#24171a;border-radius:8px;margin:.45rem 0}.login-card{max-width:520px;margin:7vh auto;padding:2.2rem;border:1px solid #30343b;border-radius:22px;background:linear-gradient(135deg,#10131a,#191d28)}.parameter{padding:1rem;border:1px solid #30343b;border-radius:14px;background:#141821;height:100%}.score{font-size:1.6rem;font-weight:800}.bar{height:7px;background:#2a2f39;border-radius:10px;overflow:hidden;margin:.45rem 0}.fill{height:100%;background:#6c8cff}.muted{color:#aab1bf;font-size:.82rem}
</style>""",unsafe_allow_html=True)

for k,v in [("authenticated",False),("user_email",""),("analysis",None),("agent_messages",[])]:
    st.session_state.setdefault(k,v)
st.session_state.setdefault("project_data",{"title":"","description":"","users":"","tech":""})

if not st.session_state.authenticated:
    st.markdown("<div class='login-card'>",unsafe_allow_html=True); st.markdown("# 🔎 ProjectX-Ray"); st.caption("Create an account or sign in to your personal project workspace.")
    login,register=st.tabs(["🔐 Sign in","🆕 Create account"])
    with login:
        with st.form("login"):
            email=st.text_input("Email"); password=st.text_input("Password",type="password"); go=st.form_submit_button("Sign in",type="primary",use_container_width=True)
        if go:
            try:
                r=requests.post(LOGIN_URL,json={"email":email,"password":password},timeout=15); data=r.json()
                if data.get("authenticated"): st.session_state.authenticated=True; st.session_state.user_email=data["user"]; st.rerun()
                st.error(data.get("message","Invalid credentials."))
            except Exception as e: st.error(f"Login service unavailable: {e}")
    with register:
        with st.form("register"):
            email2=st.text_input("Email"); p1=st.text_input("Password",type="password"); p2=st.text_input("Confirm password",type="password"); create=st.form_submit_button("Create account",type="primary",use_container_width=True)
        if create:
            if p1!=p2: st.error("Passwords do not match.")
            else:
                try:
                    r=requests.post(REGISTER_URL,json={"email":email2,"password":p1},timeout=15); data=r.json()
                    if data.get("authenticated"): st.session_state.authenticated=True; st.session_state.user_email=data["user"]; st.rerun()
                    st.error(data.get("message","Could not create account."))
                except Exception as e: st.error(f"Registration service unavailable: {e}")
    st.info("Demo account: demo@projectxray.app / projectxray123"); st.markdown("</div>",unsafe_allow_html=True); st.stop()

st.markdown("<div class='hero'><h1>🔎 ProjectX-Ray</h1><p>Stress-test your project before you build it.</p><span class='pill'>Personal workspace</span><span class='pill'>100-point parameter scoring</span><span class='pill'>Explainable analysis</span></div>",unsafe_allow_html=True)
with st.sidebar:
    st.header("👤 My account"); st.write(st.session_state.user_email)
    if st.button("📚 My project history",use_container_width=True): st.session_state.show_history=True
    if st.button("🚪 Logout",use_container_width=True):
        for k in ["authenticated","user_email","analysis","agent_messages","show_history"]: st.session_state.pop(k,None)
        st.rerun()
    st.divider()
    if st.button("✨ Load example",use_container_width=True): st.session_state.project_data=random.choice(EXAMPLES); st.session_state.analysis=None; st.rerun()
    if st.button("🧹 New project",use_container_width=True): st.session_state.project_data={"title":"","description":"","users":"","tech":""}; st.session_state.analysis=None; st.rerun()

if st.session_state.get("show_history"):
    st.subheader("📚 My Project History")
    try:
        h=requests.get(f"{HISTORY_URL}/{st.session_state.user_email}",timeout=15); h.raise_for_status()
        for item in h.json():
            with st.expander(f"{item['title']} · {item['analysis']['overall_score']}/100 · {item['created_at']}"):
                st.write(item["description"]); st.caption(f"Users: {item['target_users']} · Tech: {', '.join(item['technologies']) or 'Not specified'}")
                if st.button("Open this project",key=f"open_{item['id']}"):
                    st.session_state.project_data={"title":item["title"],"description":item["description"],"users":item["target_users"],"tech":", ".join(item["technologies"])}; st.session_state.analysis=item["analysis"]; st.session_state.show_history=False; st.rerun()
        if not h.json(): st.info("No saved projects yet.")
    except Exception as e: st.error(f"Could not load history: {e}")
    st.divider()

st.subheader("1. Define your project")
with st.form("project_form"):
    title=st.text_input("Project title",value=st.session_state.project_data["title"]); description=st.text_area("What are you building?",value=st.session_state.project_data["description"],height=150)
    c1,c2=st.columns(2)
    with c1: users=st.text_input("Who will use it?",value=st.session_state.project_data["users"])
    with c2: tech=st.text_input("Technologies",value=st.session_state.project_data["tech"])
    submitted=st.form_submit_button("🚀 Stress-test my project",type="primary",use_container_width=True)
if submitted:
    if len(title.strip())<3 or len(description.strip())<20 or len(users.strip())<3: st.error("Enter a title, a description of at least 20 characters, and target users.")
    else:
        st.session_state.project_data={"title":title.strip(),"description":description.strip(),"users":users.strip(),"tech":tech.strip()}; payload={"title":title.strip(),"description":description.strip(),"target_users":users.strip(),"technologies":[x.strip() for x in tech.split(",") if x.strip()]}
        try:
            r=requests.post(f"{ANALYZE_URL}?email={st.session_state.user_email}",json=payload,timeout=35); r.raise_for_status(); st.session_state.analysis=r.json(); st.session_state.agent_messages=[]; st.success("Analysis complete and saved to your workspace.")
        except Exception as e: st.error(f"Analysis failed: {e}")

result=st.session_state.analysis
if result:
    st.divider(); st.subheader(f"2. ProjectX-Ray report — {result['project_title']}")
    cols=st.columns(6)
    for col,(label,key) in zip(cols,[("Overall","overall_score"),("Feasibility","feasibility"),("Technical risk","technical_risk"),("Originality","originality"),("Scope","scope_clarity"),("User fit","user_fit")]): col.metric(label,result[key] if isinstance(result[key],int) else result[key]["score"])

    st.markdown("### Parameters")
    st.caption("The analysis engine evaluates each parameter from the project description, target users, technologies, and detected risk signals. Every parameter receives a score out of 100.")
    params=result.get("parameters",[])
    if params:
        for start in range(0,len(params),3):
            row=st.columns(3)
            for col,item in zip(row,params[start:start+3]):
                name=item["name"]; score=item["score"]; icon=PARAMETER_ICONS.get(name,"⚪"); reason=item.get("reasons",["Based on submitted project evidence."])[0]
                with col:
                    st.markdown(f"<div class='parameter'><b>{icon} {name}</b><div class='score'>{score}/100</div><div class='muted'>{item['level']}</div><div class='bar'><div class='fill' style='width:{score}%'></div></div><div class='muted'>{reason}</div></div>",unsafe_allow_html=True)
    else: st.info("Run a fresh analysis to generate parameter scores.")

    st.info(f"**Verdict:** {result['verdict']} · **Confidence:** {result['confidence']}/100")
    left,right=st.columns(2)
    with left:
        st.markdown("### 🎯 Why these scores?")
        for key,label in [("feasibility","Feasibility"),("technical_risk","Technical risk"),("originality","Originality"),("scope_clarity","Scope clarity"),("user_fit","User fit")]:
            item=result[key]; st.markdown(f"**{label}: {item['score']}/100 — {item['level']}**"); [st.markdown(f"- {x}") for x in item["reasons"]]
    with right:
        st.markdown("### 💡 Recommendations")
        for i,rec in enumerate(result["recommendations"],1): st.markdown(f"<div class='rec'><b>{i}.</b> {rec}</div>",unsafe_allow_html=True)
        for flag in result["risk_flags"]: st.markdown(f"<div class='risk'><b>{flag['severity'].upper()}</b> · {flag['category']}<br>{flag['message']}</div>",unsafe_allow_html=True)
    st.divider(); st.subheader("3. 🤖 Ask the recommendation agent")
    for m in st.session_state.agent_messages:
        with st.chat_message(m["role"]): st.markdown(m["content"]); [st.markdown(f"- {s}") for s in m.get("steps",[])]
    q=st.chat_input("What should I build first? How can I improve originality?")
    if q:
        st.session_state.agent_messages.append({"role":"user","content":q}); project={"title":st.session_state.project_data["title"],"description":st.session_state.project_data["description"],"target_users":st.session_state.project_data["users"],"technologies":[x.strip() for x in st.session_state.project_data["tech"].split(",") if x.strip()]}
        try:
            r=requests.post(RECOMMEND_URL,json={"project":project,"analysis":result,"question":q},timeout=35); r.raise_for_status(); d=r.json(); st.session_state.agent_messages.append({"role":"assistant","content":d["answer"],"steps":d.get("next_steps",[])}); st.rerun()
        except Exception as e: st.error(f"Agent unavailable: {e}")
else: st.info("Submit a project to generate your explainable report and parameter scores.")
