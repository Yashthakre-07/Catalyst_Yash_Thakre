import streamlit as st
import time
import os
from dotenv import load_dotenv
load_dotenv()

from ui_styles import CSS, ORBS
from utils.file_handler import extract_text_from_pdf, save_json_to_file
from agent.core import AssessmentAgent
from utils.pdf_generator import generate_plan_pdf

# ── Page Config ────────────────────────────────────────
st.set_page_config(
    page_title="NeuralHire",
    page_icon="◈", layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(CSS, unsafe_allow_html=True)
st.markdown(ORBS, unsafe_allow_html=True)

# ── Session State ──────────────────────────────────────
if "phase" not in st.session_state:
    st.session_state.phase = "hero"
    st.session_state.jd_text = ""
    st.session_state.resume_text = ""
    st.session_state.messages = []
    st.session_state.skill_assessments = []
    st.session_state.agent = AssessmentAgent()

# ── Components ─────────────────────────────────────────
def render_nav(active: int):
    steps = ["Requirement", "Candidate", "Assessment", "Intelligence"]
    fill = (active / (len(steps)-1)) * 100
    nodes = ""
    for i, s in enumerate(steps):
        cls = "nav-node " + ("complete" if i < active else "active" if i == active else "")
        inner = "✓" if i < active else str(i+1)
        nodes += f'<div class="nav-step"><div class="{cls}">{inner}</div><span class="nav-label {"active" if i == active else ""}">{s}</span></div>'
    st.markdown(f'<div class="nav-container"><div class="nav-track-bg"><div class="nav-track-fill" style="width:{fill}%"></div></div><div class="nav-nodes">{nodes}</div></div>', unsafe_allow_html=True)

def render_processing(text: str):
    gear_svg = '<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M41.7 13.5L46.9 3.2C48.8 3.5 50.7 4 52.4 4.5L52.8 16.1C55.6 17.2 58.2 18.7 60.5 20.6L70.1 13.9C71.3 15.3 72.5 16.8 73.5 18.4L66.3 27C67.9 29.5 69.1 32.2 69.8 35.1L81.2 36.3C81 38.3 80.6 40.2 80 42H68.3C67.3 45 65.6 47.7 63.5 50.1L70.8 59.1C69.3 60.4 67.7 61.6 66 62.6L57.9 54.7C55.2 56.4 52.3 57.7 49.2 58.5L48 70C46.1 69.8 44.1 69.3 42.4 68.8L41.9 57.1C39.1 56 36.5 54.5 34.2 52.6L24.6 59.3C23.4 57.9 22.2 56.4 21.2 54.8L28.4 46.2C26.8 43.7 25.6 41 24.9 38.1L13.5 36.9C13.7 34.9 14.1 33 14.7 31.2H26.4C27.4 28.2 29.1 25.5 31.2 23.1L23.9 14.1C25.4 12.8 27 11.6 28.7 10.6L36.8 18.5C39.5 16.8 42.4 15.5 45.5 14.7L41.7 13.5ZM47.4 48C53.6 48 58.7 42.9 58.7 36.6C58.7 30.4 53.6 25.3 47.4 25.3C41.2 25.3 36.1 30.4 36.1 36.6C36.1 42.9 41.2 48 47.4 48Z" fill="url(#g1)"/><defs><linearGradient id="g1" x1="13" y1="3" x2="81" y2="70" gradientUnits="userSpaceOnUse"><stop stop-color="#7C6AF7"/><stop offset="1" stop-color="#A78BFA"/></linearGradient></defs></svg>'
    gear_svg_s = '<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M41.7 13.5L46.9 3.2C48.8 3.5 50.7 4 52.4 4.5L52.8 16.1C55.6 17.2 58.2 18.7 60.5 20.6L70.1 13.9C71.3 15.3 72.5 16.8 73.5 18.4L66.3 27C67.9 29.5 69.1 32.2 69.8 35.1L81.2 36.3C81 38.3 80.6 40.2 80 42H68.3C67.3 45 65.6 47.7 63.5 50.1L70.8 59.1C69.3 60.4 67.7 61.6 66 62.6L57.9 54.7C55.2 56.4 52.3 57.7 49.2 58.5L48 70C46.1 69.8 44.1 69.3 42.4 68.8L41.9 57.1C39.1 56 36.5 54.5 34.2 52.6L24.6 59.3C23.4 57.9 22.2 56.4 21.2 54.8L28.4 46.2C26.8 43.7 25.6 41 24.9 38.1L13.5 36.9C13.7 34.9 14.1 33 14.7 31.2H26.4C27.4 28.2 29.1 25.5 31.2 23.1L23.9 14.1C25.4 12.8 27 11.6 28.7 10.6L36.8 18.5C39.5 16.8 42.4 15.5 45.5 14.7L41.7 13.5ZM47.4 48C53.6 48 58.7 42.9 58.7 36.6C58.7 30.4 53.6 25.3 47.4 25.3C41.2 25.3 36.1 30.4 36.1 36.6C36.1 42.9 41.2 48 47.4 48Z" fill="url(#g2)"/><defs><linearGradient id="g2" x1="13" y1="3" x2="81" y2="70" gradientUnits="userSpaceOnUse"><stop stop-color="#10B981"/><stop offset="1" stop-color="#34D399"/></linearGradient></defs></svg>'
    st.markdown(f'<div class="neural-core-container"><div class="gear-wrapper"><div class="core-glow"></div><div class="gear gear-large">{gear_svg}</div><div class="gear gear-small">{gear_svg_s}</div></div><div class="fascinating-text">{text}</div></div>', unsafe_allow_html=True)

def trigger_first_question():
    """Auto-ask the first question when entering assessment for a new skill."""
    agent = st.session_state.agent
    skill = agent.get_current_skill()
    if not skill:
        return
    skill_name = skill["skill_name"]
    
    # Check if we already have an assistant question for this skill
    already_asked = any(m.get("skill") == skill_name and m.get("role") == "assistant" for m in st.session_state.messages)
    
    if not already_asked:
        with st.status(f"◈ Establishing Neural Link for {skill_name}...", expanded=False):
            decision = agent.get_next_question()
            if decision.get("type") == "question":
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": decision["content"],
                    "skill": skill_name
                })
                st.write("Link established.")
            else:
                # Skill skipped or completed immediately
                agent.score_current_skill()
                st.write("Skill context sufficient. Synchronizing next node...")
        st.rerun() 

# ══════════════════════════════════════════════════════
# PHASE: HERO
# ══════════════════════════════════════════════════════
if st.session_state.phase == "hero":
    st.markdown('<div class="hero-full"><div class="hero-badge"><div class="dot"></div>Neural Sync Active</div><h1 class="hero-title-god">Neural<br><span>Hire.</span></h1><p class="hero-subtitle-god" style="font-size:18px;">Autonomous skill assessment engine.</p></div>', unsafe_allow_html=True)
    _, c, _ = st.columns([1, 0.4, 1])
    with c:
        if st.button("Initiate Scan", key="hero_btn"):
            st.session_state.phase = "step_jd"
            st.rerun()

# ══════════════════════════════════════════════════════
# PHASE: JD UPLOAD
# ══════════════════════════════════════════════════════
elif st.session_state.phase == "step_jd":
    render_nav(0)
    with st.container(border=True):
        st.markdown('<div class="section-label">Phase 01</div><h1 class="section-title-best">The <span style="color:var(--accent)">Requirement.</span></h1><p style="color:var(--text-muted); font-size:12px; margin-bottom:1.5rem;">Vectorizing Job Description.</p>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["◈ Input", "◈ Payload"])
        jd_input = ""
        with tab1:
            jd_input = st.text_area("JD", placeholder="Paste JD here...", height=150, label_visibility="collapsed")
        with tab2:
            st.markdown('<div style="border:1px dashed rgba(124,106,247,0.2); border-radius:12px; padding:2rem; text-align:center; color:var(--text-muted); font-size:12px;">✦ Drop Payload</div>', unsafe_allow_html=True)
            jd_file = st.file_uploader("JD PDF", type=["pdf"], label_visibility="collapsed")
            if jd_file: jd_input = extract_text_from_pdf(jd_file.read())

        st.markdown("<div style='margin-top:1.25rem;'>", unsafe_allow_html=True)
        if st.button("Analyze Requirement", key="jd_next", use_container_width=True):
            if jd_input and jd_input.strip():
                st.session_state.jd_text = jd_input
                st.session_state.phase = "processing_jd"
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# PHASE: RESUME UPLOAD
# ══════════════════════════════════════════════════════
elif st.session_state.phase == "step_resume":
    render_nav(1)
    with st.container(border=True):
        st.markdown('<div class="section-label">Phase 02</div><h1 class="section-title-best">The <span style="color:var(--emerald)">Candidate.</span></h1><p style="color:var(--text-muted); font-size:12px; margin-bottom:1.5rem;">Decoding Profile Alignment.</p>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["◈ Input", "◈ Payload"])
        res_input = ""
        with tab1:
            res_input = st.text_area("Res", placeholder="Paste Resume here...", height=150, label_visibility="collapsed")
        with tab2:
            st.markdown('<div style="border:1px dashed rgba(16,185,129,0.2); border-radius:12px; padding:2rem; text-align:center; color:var(--text-muted); font-size:12px;">◈ Drop Payload</div>', unsafe_allow_html=True)
            res_file = st.file_uploader("Res PDF", type=["pdf"], label_visibility="collapsed")
            if res_file: res_input = extract_text_from_pdf(res_file.read())

        st.markdown("<div style='margin-top:1.25rem;'>", unsafe_allow_html=True)
        c_back, c_next = st.columns([0.4, 1.6])
        with c_back:
            if st.button("Back", key="rb", use_container_width=True):
                st.session_state.phase = "step_jd"; st.rerun()
        with c_next:
            if st.button("Initiate Assessment", key="rn", use_container_width=True):
                if res_input and res_input.strip():
                    st.session_state.resume_text = res_input
                    st.session_state.phase = "processing_resume"
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# PROCESSING ANIMATIONS
# ══════════════════════════════════════════════════════
elif st.session_state.phase == "processing_jd":
    render_nav(0); render_processing("Contextualizing Requirement..."); time.sleep(3)
    st.session_state.phase = "step_resume"; st.rerun()

elif st.session_state.phase == "processing_resume":
    render_nav(1); render_processing("Decoding Neural Alignment..."); time.sleep(3)
    st.session_state.agent.parse_documents(st.session_state.resume_text, st.session_state.jd_text)
    st.session_state.messages = []  # Clear messages for fresh assessment
    st.session_state.phase = "assessing"; st.rerun()

# ══════════════════════════════════════════════════════
# ASSESSMENT (THE CORE FIX)
# ══════════════════════════════════════════════════════
elif st.session_state.phase == "assessing":
    render_nav(2)
    agent = st.session_state.agent
    skills = agent.required_skills
    idx = agent.current_skill_index

    # All skills done -> go to results
    if not skills:
        st.error("No skills identified for assessment. Please check your Job Description.")
        if st.button("Re-evaluate Requirement"):
            st.session_state.phase = "step_jd"; st.rerun()
        st.stop()

    if idx >= len(skills):
        st.session_state.phase = "generating_results"
        st.rerun()

    current_skill = skills[idx]
    skill_name = current_skill["skill_name"]

    # Filter messages for current skill ONLY
    current_messages = [m for m in st.session_state.messages if m.get("skill") == skill_name]

    # ── Header: Cinematic Skill Info ──
    st.markdown(f'''
        <div style="display:flex; flex-direction:column; align-items:center; margin-bottom:2rem; animation: fadeIn 0.8s ease-out;">
            <div class="section-label">ACTIVE NEURAL LINK</div>
            <h1 style="margin:0; font-size:48px; font-weight:800; background:linear-gradient(to right, #FFF, var(--accent), var(--emerald)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; text-align:center;">
                {skill_name}
            </h1>
            <div style="margin-top:0.8rem; display:flex; gap:10px; align-items:center;">
                <div style="height:4px; width:100px; background:rgba(255,255,255,0.1); border-radius:2px; overflow:hidden;">
                    <div style="height:100%; width:{(idx+1)/len(skills)*100}%; background:var(--accent);"></div>
                </div>
                <span style="font-family:JetBrains Mono; color:var(--text-muted); font-size:11px; letter-spacing:0.1em;">
                    NODE {idx+1} OF {len(skills)}
                </span>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    # ── Chat Area ──
    chat_container = st.container(height=450)
    should_rerun = False
    with chat_container:
        if not current_messages:
            st.markdown(f'<div style="text-align:center; color:var(--text-muted); padding:3rem; font-style:italic;">Initializing intelligence probe for {skill_name}...</div>', unsafe_allow_html=True)
            # AUTO-ASK (Synchronous for the first time)
            try:
                with st.spinner("Establishing Connection..."):
                    try:
                        decision = agent.get_next_question()
                    except Exception as e:
                        st.error(f"◈ NEURAL LINK FAILURE: {str(e)}")
                        st.info("The AI engine is currently unreachable. This is usually due to rate limits or invalid keys in your .env file.")
                        st.stop()
                    if decision.get("type") == "question":
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": decision["content"],
                            "skill": skill_name
                        })
                    else:
                        agent.score_current_skill()
                should_rerun = True
            except Exception as e:
                st.error(f"◈ Neural Link Interrupted: {e}")
                if st.button("Retry Connection"): st.rerun()
        else:
            for m in current_messages:
                with st.chat_message(m["role"]):
                    st.markdown(m["content"])
    
    if should_rerun:
        st.rerun()

    # ── User Input ──
    u_in = st.chat_input(f"Speak to the Agent about {skill_name}...")
    if u_in:
        st.session_state.messages.append({"role": "user", "content": u_in, "skill": skill_name})
        agent.process_answer(u_in)
        with st.spinner("Analyzing Answer..."):
            decision = agent.get_next_question()
            if decision.get("type") == "question":
                st.session_state.messages.append({"role": "assistant", "content": decision["content"], "skill": skill_name})
            else:
                agent.score_current_skill()
                if agent.current_skill_index < len(skills):
                    next_skill = skills[agent.current_skill_index]["skill_name"]
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"◈ Intelligence scan for **{skill_name}** complete. Moving to **{next_skill}**...",
                        "skill": skill_name 
                    })
                else:
                    st.session_state.phase = "generating_results"
        st.rerun()

    # ── Action Buttons ──
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Skip Skill →", key="skip_skill", use_container_width=True):
            agent.score_current_skill()
            st.rerun()
    with c2:
        if st.button("Finish All →", key="finish_all", use_container_width=True):
            while agent.current_skill_index < len(skills):
                agent.score_current_skill()
            st.session_state.phase = "generating_results"
            st.rerun()

# ══════════════════════════════════════════════════════
# RESULTS
# ══════════════════════════════════════════════════════
elif st.session_state.phase == "generating_results":
    render_nav(3)
    
    # Immersive status rotation
    status_placeholder = st.empty()
    statuses = [
        "Synthesizing Assessment Intelligence...",
        "Analysing Technical Gaps...",
        "Building Personalised Skill Leveraging Map...",
        "Generating Weekly Daily Breakdown...",
        "Curating High-Impact Resources...",
        "Finalising Your Intelligence Dashboard..."
    ]
    
    # We do the work while showing statuses
    with st.spinner("Processing..."):
        for i, status in enumerate(statuses):
            status_placeholder.markdown(f"""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 300px;">
                <div class="processing-icon" style="font-size: 48px; margin-bottom: 20px;">◈</div>
                <div style="font-family: 'JetBrains Mono'; color: var(--accent); letter-spacing: 0.1em; font-size: 14px; text-transform: uppercase;">Phase {i+1}/6</div>
                <div style="font-size: 20px; font-weight: 700; margin-top: 10px;">{status}</div>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(1.5)
            if i == 0: # Do actual work in the first step or throughout
                st.session_state.learning_plan = st.session_state.agent.generate_plan()
    
    st.session_state.phase = "results"
    st.rerun()

elif st.session_state.phase == "results":
    # Restore cinematic dark shell for results
    st.markdown("""
        <style>
        html, body, .stApp { 
            overflow: auto !important; 
            height: auto !important; 
            background: radial-gradient(circle at top right, #0F172A, #020617) !important;
            color: #F8FAFC !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] { 
            max-width: 1200px !important; 
            margin: 0 auto !important; 
            background: transparent !important;
        }
        </style>
    """, unsafe_allow_html=True)
    render_nav(3)
    
    try:
        from results_dashboard import render_dashboard
        plan = st.session_state.learning_plan
        assessments = st.session_state.agent.skill_assessments
        
        # ── PDF Download Button ──
        c1, c2 = st.columns([1, 4])
        with c1:
            pdf_buffer = generate_plan_pdf(plan)
            st.download_button(
                label="◈ DOWNLOAD PDF REPORT",
                data=pdf_buffer,
                file_name=f"NeuralPlan_{plan.candidate_name}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        
        render_dashboard(plan, assessments)
    except Exception as e:
        st.error(f"Intelligence Report rendering encountered an issue. Showing fallback view.")
        st.exception(e)
        plan = st.session_state.learning_plan
        st.json(plan.model_dump())
        if st.button("New Intelligence Scan", key="fallback_new"):
            for k in list(st.session_state.keys()): del st.session_state[k]
            from agent.core import AssessmentAgent
            st.session_state.agent = AssessmentAgent(); st.rerun()

