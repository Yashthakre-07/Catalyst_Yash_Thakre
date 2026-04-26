"""
results_dashboard.py — Mastery Intelligence Dashboard.
Features: Neural Skill Tabs, Week-by-Week Steppers, and 2x2 Resource Grids.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import html

from models.learning_plan import LearningPlan
from models.skill import SkillAssessment

# ─── Color System (Neural Dark) ──────────────────────────
C_STRONG = "#639922"      # Neural Green
C_DEVELOPING = "#EF9F27"  # Neural Amber
C_GAP = "#E24B4A"         # Neural Red
C_TEXT = "#F8FAFC"
C_MUTED = "#94A3B8"
C_ACCENT = "#7C6AF7"      # Neural Purple
C_CARD_BG = "rgba(15, 23, 42, 0.7)"
C_BORDER = "rgba(255, 255, 255, 0.1)"

def _cat_color(category: str) -> str:
    return {
        "STRONG": C_STRONG,
        "DEVELOPING": C_DEVELOPING,
        "GAP": C_GAP,
    }.get(category, C_MUTED)

def _plotly_layout(fig, height=400):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=C_TEXT, size=13),
        margin=dict(l=20, r=20, t=40, b=20),
        height=height,
        showlegend=True
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.1)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.1)")
    return fig

def render_dashboard(plan: LearningPlan, assessments: list[SkillAssessment]):
    # Global CSS for Mastery UI
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500&display=swap');
    
    /* Neural Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px !important;
        background-color: transparent !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px 12px 0 0 !important;
        padding: 10px 20px !important;
        color: {C_MUTED} !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: rgba(124, 106, 247, 0.1) !important;
        border-color: {C_ACCENT} !important;
        color: {C_TEXT} !important;
    }}
    
    /* Skill Header */
    .skill-header {{
        background: linear-gradient(135deg, rgba(124, 106, 247, 0.1), rgba(15, 23, 42, 0.5)) !important;
        border: 1px solid {C_BORDER} !important;
        border-radius: 20px !important;
        padding: 2rem !important;
        margin-bottom: 2rem !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
    }}
    
    /* Resource Grid */
    .res-grid {{
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 1.5rem !important;
    }}
    .res-box {{
        background: rgba(255,255,255,0.02) !important;
        border: 1px solid {C_BORDER} !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        height: 100% !important;
    }}
    .res-box-title {{
        font-size: 16px !important;
        font-weight: 900 !important;
        color: {C_ACCENT} !important;
        text-transform: uppercase !important;
        letter-spacing: 0.15em !important;
        margin-bottom: 1.5rem !important;
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
    }}
    .res-box-title::before {{
        content: "◆" !important;
        color: {C_STRONG} !important;
    }}
    
    /* YouTube Levels - EYE TAKING */
    .yt-level-card {{
        background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(0,0,0,0.6)) !important;
        border: 2px solid rgba(255,255,255,0.1) !important;
        border-radius: 20px !important;
        padding: 1.8rem !important;
        margin-bottom: 1.2rem !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        position: relative !important;
        overflow: hidden !important;
    }}
    .yt-level-card:hover {{
        border-color: {C_ACCENT} !important;
        transform: scale(1.02) translateY(-5px) !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.4), 0 0 20px rgba(124, 106, 247, 0.2) !important;
    }}
    .yt-level-tag {{
        font-size: 14px !important;
        font-weight: 900 !important;
        letter-spacing: 0.2em !important;
        margin-bottom: 12px !important;
        text-shadow: 0 0 10px rgba(255,255,255,0.2) !important;
    }}
    .yt-title {{
        font-size: 22px !important;
        font-weight: 900 !important;
        line-height: 1.2 !important;
        color: white !important;
        text-decoration: none !important;
        display: block !important;
        margin-bottom: 10px !important;
    }}
    .yt-meta {{
        font-size: 15px !important;
        color: {C_MUTED} !important;
        background: rgba(0,0,0,0.3) !important;
        padding: 8px 12px !important;
        border-radius: 10px !important;
        display: inline-block !important;
    }}
    
    /* ANIMATIONS FOR EYE CATCHING */
    @keyframes float {{
        0% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-10px); }}
        100% {{ transform: translateY(0px); }}
    }}
    .pulse-glow {{
        animation: pulseGlow 3s infinite alternate ease-in-out !important;
    }}
    @keyframes pulseGlow {{
        from {{ box-shadow: 0 0 5px rgba(124, 106, 247, 0.2); }}
        to {{ box-shadow: 0 0 25px rgba(124, 106, 247, 0.5); }}
    }}

    .report-card {{
        background: {C_CARD_BG} !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid {C_BORDER} !important;
        border-radius: 24px !important;
        padding: 2.5rem !important;
        margin-bottom: 2rem !important;
    }}
    .metric-pill {{
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 18px 24px !important;
        text-align: center !important;
        flex: 1 !important;
    }}
    .metric-value {{ font-size: 36px !important; font-weight: 800 !important; color: {C_TEXT} !important; }}
    .metric-label {{ font-size: 13px !important; font-weight: 700 !important; color: {C_MUTED} !important; text-transform: uppercase !important; letter-spacing: 0.15em !important; }}
    
    .section-title {{
        font-size: 16px !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.2em !important;
        color: {C_ACCENT} !important;
        margin: 4rem 0 2rem !important;
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
    }}
    .section-title::after {{ content: ""; flex: 1; height: 1px; background: linear-gradient(to right, {C_ACCENT}, transparent); }}
    
    .badge {{ padding: 8px 16px !important; border-radius: 10px !important; font-size: 13px !important; font-weight: 800 !important; text-transform: uppercase !important; }}
    .badge-strong {{ background: rgba(99, 153, 34, 0.15) !important; color: {C_STRONG} !important; border: 1px solid {C_STRONG} !important; }}
    .badge-developing {{ background: rgba(239, 159, 39, 0.15) !important; color: {C_DEVELOPING} !important; border: 1px solid {C_DEVELOPING} !important; }}
    .badge-gap {{ background: rgba(226, 75, 74, 0.15) !important; color: {C_GAP} !important; border: 1px solid {C_GAP} !important; }}
    </style>
    """, unsafe_allow_html=True)

    _block1_header(plan, assessments)
    
    c_bar, c_radar = st.columns([1.2, 1], gap="large")
    with c_bar: _block2_bar_chart(plan)
    with c_radar: _block3_radar(plan)

    _block4_leverage_cards(plan)
    _block5_timeline(plan)
    
    c_ready, c_motiv = st.columns([1, 1.5], gap="large")
    with c_ready: _block7_readiness(plan)
    with c_motiv: _block8_motivation(plan)

    st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)

def _block1_header(plan: LearningPlan, assessments: list[SkillAssessment]):
    try:
        gaps = sum(1 for sp in plan.skills if sp.category == "GAP")
        n_skills = len(plan.skills)
        name = html.escape(getattr(plan, 'candidate_name', 'Candidate'))
        role = html.escape(getattr(plan, 'target_role', 'Target Role'))
        weeks = getattr(plan, 'total_weeks', 0)
        score = getattr(plan, 'readiness_score', 0)

        st.markdown(f"""
        <div class="report-card">
            <h1 style="margin:0; font-size: 48px; font-weight: 800; background: linear-gradient(45deg, #FFF, {C_ACCENT}); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{name}</h1>
            <div style="color: {C_STRONG}; font-weight: 800; font-size: 14px; text-transform: uppercase; letter-spacing: 0.2em; margin-top: 6px;">{role}</div>
            <div style="display: flex; gap: 14px; flex-wrap: wrap; margin-top: 2rem;">
                <div class="metric-pill"><div class="metric-value">{weeks}w</div><div class="metric-label">Timeline</div></div>
                <div class="metric-pill"><div class="metric-value">{n_skills}</div><div class="metric-label">Nodes</div></div>
                <div class="metric-pill"><div class="metric-value" style="color:{C_GAP}">{gaps}</div><div class="metric-label">Gaps</div></div>
                <div class="metric-pill"><div class="metric-value" style="color:{C_STRONG}">{score}%</div><div class="metric-label">Ready</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e: st.error(f"Header Error: {e}")

def _block2_bar_chart(plan: LearningPlan):
    try:
        st.markdown('<div class="section-title">Gap Analysis</div>', unsafe_allow_html=True)
        if not plan.skills: st.info("No data available."); return

        data = []
        for sp in plan.skills:
            data.append({
                "Skill": sp.skill_name,
                "Level": getattr(sp, 'current_level', 0),
                "Target": getattr(sp, 'target_level', 10),
                "Category": sp.category,
                "Color": _cat_color(sp.category)
            })
        
        df = pd.DataFrame(data)
        fig = go.Figure()
        fig.add_trace(go.Bar(y=df["Skill"], x=df["Level"], orientation='h', marker=dict(color=df["Color"]), text=df["Category"], textposition="auto"))
        for i, row in df.iterrows():
            fig.add_shape(type="line", x0=row["Target"], x1=row["Target"], y0=i-0.4, y1=i+0.4, line=dict(color="white", width=2, dash="dot"))
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(_plotly_layout(fig, height=max(300, len(df)*45)), use_container_width=True)
    except Exception as e: st.error(f"Bar Error: {e}")

def _block3_radar(plan: LearningPlan):
    try:
        st.markdown('<div class="section-title">Competency Map</div>', unsafe_allow_html=True)
        if not plan.skills or len(plan.skills) < 2: st.info("Need more skills for radar."); return

        skills = [sp.skill_name for sp in plan.skills]
        assessed = [getattr(sp, 'current_level', 0) for sp in plan.skills]
        required = [getattr(sp, 'target_level', 10) for sp in plan.skills]
        
        if len(skills) >= 3: skills += [skills[0]]; assessed += [assessed[0]]; required += [required[0]]
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=required, theta=skills, fill='toself', fillcolor='rgba(255,255,255,0.02)', line=dict(color="rgba(255,255,255,0.2)", width=1, dash='dot'), name='Target'))
        fig.add_trace(go.Scatterpolar(r=assessed, theta=skills, fill='toself', fillcolor='rgba(99,153,34,0.2)', line=dict(color=C_STRONG, width=3), name='Actual'))
        fig.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=True, range=[0, 10])))
        st.plotly_chart(_plotly_layout(fig, height=400), use_container_width=True)
    except Exception as e: st.error(f"Radar Error: {e}")

def _block4_leverage_cards(plan: LearningPlan):
    try:
        leverages = getattr(plan, 'adjacent_leverages', [])
        if not leverages: return
        st.markdown('<div class="section-title">Intelligence Insights</div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for i, lev in enumerate(leverages):
            with cols[i % 2]:
                es = html.escape(lev.existing_skill)
                us = html.escape(lev.unlocks_skill)
                msg = html.escape(lev.message)
                st.markdown(f'<div style="background:rgba(255,255,255,0.02); border:1px solid {C_BORDER}; border-left:4px solid {C_STRONG}; border-radius:16px; padding:2rem; margin-bottom:1.5rem;"><div style="font-weight:800; font-size:14px; color:{C_TEXT};">{es} → {us}</div><div style="font-size:12px; color:{C_MUTED};">{msg}</div></div>', unsafe_allow_html=True)
    except Exception as e: st.error(f"Leverage Error: {e}")

def _block5_timeline(plan: LearningPlan):
    try:
        st.markdown('<div class="section-title">Strategic Roadmap</div>', unsafe_allow_html=True)
        if not plan.skills: st.info("No timeline data."); return

        # 1. Gantt Chart
        base = datetime(2025, 1, 1); rows = []; current_w = 1
        for sp in plan.skills:
            weeks = getattr(sp, 'total_weeks', 2)
            if weeks == 0 and sp.category == "STRONG": weeks = 1 # Show 1 week for strong skills to keep on chart
            rows.append(dict(Skill=sp.skill_name, Start=base + pd.Timedelta(weeks=current_w - 1), Finish=base + pd.Timedelta(weeks=current_w + weeks - 1), Category=sp.category))
            current_w += weeks
            
        df = pd.DataFrame(rows)
        fig = px.timeline(df, x_start="Start", x_end="Finish", y="Skill", color="Category", color_discrete_map={"GAP": C_GAP, "DEVELOPING": C_DEVELOPING, "STRONG": C_STRONG})
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(_plotly_layout(fig, height=max(200, len(rows)*40 + 80)), use_container_width=True)

        # 2. Skill Tabs Overhaul
        st.markdown('<div style="height: 40px;"></div>', unsafe_allow_html=True)
        def get_dot(cat): return "🔴" if cat == "GAP" else "🟠" if cat == "DEVELOPING" else "🟢"
        tab_labels = [f"{get_dot(sp.category)} {sp.skill_name}" for sp in plan.skills]
        tabs = st.tabs(tab_labels)

        for i, (tab, sp) in enumerate(zip(tabs, plan.skills)):
            with tab:
                adj_skills = getattr(sp, 'adjacent_skills', [])
                adj_html = " ".join([f"<span style='background:rgba(255,255,255,0.05); border:1px solid {C_BORDER}; border-radius:6px; padding:4px 8px; font-size:10px; color:{C_MUTED};'>#{html.escape(s)}</span>" for s in adj_skills])
                
                sp_name = html.escape(sp.skill_name)
                st.markdown(f'<div class="skill-header"><div><div style="font-size:10px; font-weight:800; color:{C_MUTED}; text-transform:uppercase; letter-spacing:0.2em;">COGNITIVE NODE</div><div style="font-size:32px; font-weight:800; color:{C_TEXT};">{sp_name}</div><div style="display:flex; gap:8px; margin-top:12px;">{adj_html}</div></div><div style="text-align:right;"><div class="badge badge-{sp.category.lower()}">{sp.category}</div><div style="font-size:24px; font-weight:800; color:{C_TEXT}; margin-top:10px;">{sp.total_weeks} <span style="font-size:12px; color:{C_MUTED};">WEEKS</span></div></div></div>', unsafe_allow_html=True)
                
                # --- NEW FEEDBACK SECTION ---
                feedback = getattr(sp, 'candidate_feedback', "")
                if feedback:
                    st.markdown(f'''
                        <div style="background: rgba(124, 106, 247, 0.03); border: 1px dashed {C_ACCENT}; border-radius: 16px; padding: 1.5rem; margin-bottom: 2rem;">
                            <div style="font-size: 11px; font-weight: 900; color: {C_ACCENT}; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.8rem; display: flex; align-items: center; gap: 8px;">
                                <span style="font-size: 16px;">◈</span> PERSONALIZED FEEDBACK
                            </div>
                            <div style="font-size: 15px; line-height: 1.6; color: {C_TEXT}; font-style: italic;">
                                "{html.escape(feedback)}"
                            </div>
                        </div>
                    ''', unsafe_allow_html=True)
                # ----------------------------

                if sp.category == "STRONG":
                    st.success("Mastery verified. Stay sharp with advanced internals."); continue
                
                topics = getattr(sp, 'topics', [])
                if not topics: 
                    st.info("Curriculum details pending synthesis."); continue

                week_labels = [t.week_label for t in topics]
                sel_w = st.radio(f"Select Week for {sp.skill_name}", week_labels, horizontal=True, label_visibility="collapsed", key=f"sel_{sp.skill_name}")
                topic = next((t for t in topics if t.week_label == sel_w), topics[0])
                
                _render_week_content(topic, sp.skill_name)
    except Exception as e: st.error(f"Timeline Error: {e}")

def _render_week_content(topic, skill_id):
    t_title = html.escape(topic.title)
    t_obj = html.escape(topic.objective)
    st.markdown(f'<div style="background:rgba(124, 106, 247, 0.05); border-left:4px solid {C_ACCENT}; padding:1.5rem; border-radius:0 16px 16px 0; margin-bottom:2rem;"><div style="font-size:10px; font-weight:800; color:{C_ACCENT}; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:4px;">OBJECTIVE: {t_title}</div><div style="font-size:16px; color:{C_TEXT}; font-weight:600;">{t_obj}</div></div>', unsafe_allow_html=True)
    with st.expander("📖 WHAT TO STUDY THIS WEEK", expanded=True):
        for i, item in enumerate(topic.what_to_study): st.markdown(f"{i+1}. {html.escape(item)}")

    col1, col2 = st.columns(2)
    with col1:
        docs_html = "".join([f"<div style='margin-bottom:20px;'><a href='{html.escape(d.url)}' target='_blank' style='color:{C_TEXT}; font-weight:800; text-decoration:none; font-size:18px; border-bottom: 1px solid rgba(255,255,255,0.1);'>{html.escape(d.title)}</a><div style='font-size:15px; color:{C_MUTED}; margin-top:6px; line-height:1.5;'>{html.escape(d.description)}</div></div>" for d in topic.documentation])
        st.markdown(f'<div class="res-box"><div class="res-box-title">Official Documentation</div>{docs_html}</div>', unsafe_allow_html=True)
        st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)
        assets_html = "".join([f"<div style='margin-bottom:15px; padding: 12px; background: rgba(124, 106, 247, 0.05); border-radius: 10px;'><span class='badge' style='background:rgba(124, 106, 247, 0.2); border:1px solid {C_ACCENT}; font-size:11px; padding:4px 10px; margin-right:10px;'>{html.escape(r.type).upper()}</span> <a href='{html.escape(r.url)}' target='_blank' style='color:{C_TEXT}; font-weight:800; text-decoration:none; font-size:16px;'>{html.escape(r.title)}</a></div>" for r in topic.extra_resources])
        st.markdown(f'<div class="res-box"><div class="res-box-title">Deep Dive Assets</div>{assets_html}</div>', unsafe_allow_html=True)
    with col2:
        yt = topic.youtube
        st.markdown(f"""
        <div class="res-box pulse-glow" style="border-top: 4px solid {C_GAP};">
            <div class="res-box-title" style="color: {C_GAP} !important;">🔥 Visual Intelligence (3 Levels)</div>
            <div class="yt-level-card">
                <div class="yt-level-tag" style="color:{C_STRONG}">⚡ LEVEL 1: EASY</div>
                <a href="{html.escape(yt.easy.url)}" target="_blank" class="yt-title">{html.escape(yt.easy.title)}</a>
                <div class="yt-meta">📺 {html.escape(yt.easy.channel)} • <span style="color:{C_STRONG}; font-weight:900;">{html.escape(yt.easy.why)}</span></div>
            </div>
            <div class="yt-level-card">
                <div class="yt-level-tag" style="color:{C_DEVELOPING}">🚀 LEVEL 2: MEDIUM</div>
                <a href="{html.escape(yt.medium.url)}" target="_blank" class="yt-title">{html.escape(yt.medium.title)}</a>
                <div class="yt-meta">📺 {html.escape(yt.medium.channel)} • <span style="color:{C_DEVELOPING}; font-weight:900;">{html.escape(yt.medium.why)}</span></div>
            </div>
            <div class="yt-level-card">
                <div class="yt-level-tag" style="color:{C_GAP}">💀 LEVEL 3: HARD</div>
                <a href="{html.escape(yt.hard.url)}" target="_blank" class="yt-title">{html.escape(yt.hard.title)}</a>
                <div class="yt-meta">📺 {html.escape(yt.hard.channel)} • <span style="color:{C_GAP}; font-weight:900;">{html.escape(yt.hard.why)}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)
        t_ho = html.escape(topic.hands_on)
        t_ms = html.escape(topic.milestone)
        st.markdown(f'<div class="res-box"><div class="res-box-title">Tactical Execution</div><div style="font-size:15px; font-weight:700; color:{C_TEXT}; margin-bottom:10px;">{t_ho}</div><div style="background:rgba(99,153,34,0.1); border:1px solid {C_STRONG}; border-radius:10px; padding:12px;"><div style="color:{C_STRONG}; font-size:10px; font-weight:800; margin-bottom:4px;">MILESTONE</div><div style="font-size:13px; color:{C_TEXT};">{t_ms}</div></div></div>', unsafe_allow_html=True)

def _block7_readiness(plan: LearningPlan):
    try:
        st.markdown('<div class="section-title">Readiness Pulse</div>', unsafe_allow_html=True)
        score = getattr(plan, 'readiness_score', 0)
        fig = go.Figure(go.Indicator(mode="gauge+number", value=score, number={'suffix': "%", 'font': {'size': 60, 'color': C_TEXT}}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': C_STRONG if score > 70 else C_DEVELOPING if score > 40 else C_GAP}, 'bgcolor': "rgba(255,255,255,0.02)", 'steps': [{'range': [0, 40], 'color': 'rgba(226,75,74,0.05)'}, {'range': [40, 70], 'color': 'rgba(239,159,39,0.05)'}, {'range': [70, 100], 'color': 'rgba(99,153,34,0.05)'}]}))
        st.plotly_chart(_plotly_layout(fig, height=250), use_container_width=True)
    except Exception as e: st.error(f"Readiness Error: {e}")

def _block8_motivation(plan: LearningPlan):
    try:
        st.markdown('<div class="section-title">Intelligence Synthesis</div>', unsafe_allow_html=True)
        summary = html.escape(getattr(plan, 'summary', 'Processing complete.'))
        st.markdown(f'<div style="background:{C_CARD_BG}; backdrop-filter:blur(20px); border:1px solid {C_BORDER}; border-radius:20px; padding:2rem; line-height:1.8; font-size:16px; border-left:6px solid {C_ACCENT};">{summary}</div>', unsafe_allow_html=True)
    except Exception as e: st.error(f"Motivation Error: {e}")
