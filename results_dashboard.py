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
# ─── Color System (GOD Tier Neural) ──────────────────────
C_STRONG = "#10B981"      # Emerald Neon
C_DEVELOPING = "#FBBF24"  # Amber Neon
C_GAP = "#F43F5E"         # Rose Neon
C_TEXT = "#FFFFFF"
C_MUTED = "#94A3B8"
C_ACCENT = "#7C6AF7"      # Electric Purple
C_CARD_BG = "rgba(10, 15, 30, 0.8)"
C_BORDER = "rgba(255, 255, 255, 0.08)"

def _cat_color(category: str) -> str:
    return {
        "STRONG": C_STRONG,
        "DEVELOPING": C_DEVELOPING,
        "GAP": C_GAP,
    }.get(category, C_MUTED)

def _plotly_layout(fig, height=450):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color=C_TEXT, size=14),
        margin=dict(l=30, r=30, t=50, b=30),
        height=height,
        showlegend=True,
        hoverlabel=dict(bgcolor="#1E293B", font_size=14, font_family="JetBrains Mono")
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.03)", zerolinecolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.03)", zerolinecolor="rgba(255,255,255,0.08)")
    return fig

def render_dashboard(plan: LearningPlan, assessments: list[SkillAssessment]):
    # Global CSS for GOD Tier Mastery UI
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }}

    /* Neural Tabs - Premium */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 12px !important;
        background-color: transparent !important;
        margin-bottom: 2rem !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        padding: 12px 28px !important;
        color: {C_MUTED} !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, rgba(124, 106, 247, 0.2), rgba(16, 185, 129, 0.1)) !important;
        border-color: {C_ACCENT} !important;
        color: white !important;
        box-shadow: 0 10px 20px -10px {C_ACCENT} !important;
        transform: translateY(-2px);
    }}
    
    /* Skill Header - GOD LEVEL */
    .skill-header {{
        background: linear-gradient(165deg, rgba(15, 23, 42, 0.9), rgba(2, 6, 23, 1)) !important;
        border: 1px solid {C_BORDER} !important;
        border-top: 2px solid {C_ACCENT} !important;
        border-radius: 32px !important;
        padding: 3rem !important;
        margin-bottom: 3rem !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        box-shadow: 0 40px 80px -20px rgba(0,0,0,0.8) !important;
    }}
    
    /* Resource Grid - Catchy */
    .res-box {{
        background: rgba(255,255,255,0.01) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid {C_BORDER} !important;
        border-radius: 24px !important;
        padding: 2rem !important;
        transition: border-color 0.3s ease !important;
    }}
    .res-box:hover {{
        border-color: rgba(124, 106, 247, 0.3) !important;
    }}
    .res-box-title {{
        font-size: 14px !important;
        font-weight: 900 !important;
        color: {C_ACCENT} !important;
        text-transform: uppercase !important;
        letter-spacing: 0.2em !important;
        margin-bottom: 2rem !important;
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
    }}
    
    /* YouTube Cards - STUNNING */
    .yt-level-card {{
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 20px !important;
        padding: 2rem !important;
        margin-bottom: 1.5rem !important;
        transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }}
    .yt-level-card:hover {{
        background: rgba(255, 255, 255, 0.04) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        transform: translateX(10px) !important;
    }}
    .yt-title {{
        font-size: 24px !important;
        font-weight: 800 !important;
        color: white !important;
        line-height: 1.3 !important;
        text-decoration: none !important;
        margin-bottom: 12px !important;
        display: block !important;
    }}

    .report-card {{
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(2, 6, 23, 0.9)) !important;
        backdrop-filter: blur(40px) !important;
        border: 1px solid {C_BORDER} !important;
        border-radius: 40px !important;
        padding: 4rem !important;
        margin-bottom: 4rem !important;
        box-shadow: 0 100px 150px -50px rgba(0, 0, 0, 0.7) !important;
    }}
    
    .metric-pill {{
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 24px !important;
        padding: 24px 32px !important;
        text-align: center !important;
        min-width: 180px !important;
    }}
    .metric-value {{ 
        font-size: 48px !important; 
        font-weight: 800 !important; 
        line-height: 1 !important;
        margin-bottom: 8px !important;
        background: linear-gradient(to bottom, #FFF, #94A3B8);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    .metric-label {{ font-size: 14px !important; font-weight: 800 !important; color: {C_MUTED} !important; text-transform: uppercase !important; letter-spacing: 0.2em !important; }}
    
    .section-title {{
        font-size: 18px !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.3em !important;
        color: {C_ACCENT} !important;
        margin: 5rem 0 3rem !important;
        display: flex !important;
        align-items: center !important;
        gap: 20px !important;
    }}
    .section-title::after {{ content: ""; flex: 1; height: 1px; background: linear-gradient(to right, {C_ACCENT}, transparent); }}
    
    .badge {{ 
        padding: 10px 20px !important; 
        border-radius: 14px !important; 
        font-size: 14px !important; 
        font-weight: 900 !important; 
        text-transform: uppercase !important; 
        letter-spacing: 0.1em !important;
    }}
    .badge-strong {{ background: rgba(16, 185, 129, 0.1) !important; color: {C_STRONG} !important; border: 1px solid rgba(16, 185, 129, 0.3) !important; box-shadow: 0 0 20px rgba(16, 185, 129, 0.1); }}
    .badge-developing {{ background: rgba(251, 191, 36, 0.1) !important; color: {C_DEVELOPING} !important; border: 1px solid rgba(251, 191, 36, 0.3) !important; }}
    .badge-gap {{ background: rgba(244, 63, 94, 0.1) !important; color: {C_GAP} !important; border: 1px solid rgba(244, 63, 94, 0.3) !important; box-shadow: 0 0 20px rgba(244, 63, 94, 0.1); }}
    </style>
    """, unsafe_allow_html=True)

    # Deduplicate skills by name (keeping the one with higher level/more info)
    seen_skills = {}
    unique_skills = []
    for sp in plan.skills:
        if sp.skill_name not in seen_skills:
            seen_skills[sp.skill_name] = sp
            unique_skills.append(sp)
        else:
            # If current one has topics and the seen one doesn't, swap
            if sp.topics and not seen_skills[sp.skill_name].topics:
                idx = unique_skills.index(seen_skills[sp.skill_name])
                unique_skills[idx] = sp
                seen_skills[sp.skill_name] = sp
    
    plan.skills = unique_skills

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
            <div style="font-size: 14px; font-weight: 900; color: {C_ACCENT}; text-transform: uppercase; letter-spacing: 0.4em; margin-bottom: 1rem;">INTELLIGENCE REPORT</div>
            <h1 style="margin:0; font-size: 84px; font-weight: 800; line-height: 0.9; letter-spacing: -0.04em; background: linear-gradient(135deg, #FFF 0%, #A78BFA 50%, #10B981 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{name}</h1>
            <div style="color: {C_MUTED}; font-weight: 600; font-size: 20px; margin-top: 1rem;">Targeting: <span style="color: {C_STRONG}; font-weight: 800;">{role}</span></div>
            
            <div style="display: flex; gap: 20px; flex-wrap: wrap; justify-content: center; margin-top: 4rem;">
                <div class="metric-pill"><div class="metric-value">{weeks}w</div><div class="metric-label">Roadmap</div></div>
                <div class="metric-pill"><div class="metric-value">{n_skills}</div><div class="metric-label">Nodes</div></div>
                <div class="metric-pill"><div class="metric-value" style="background:linear-gradient(to bottom, #F43F5E, #E11D48); -webkit-background-clip:text;">{gaps}</div><div class="metric-label">Gaps</div></div>
                <div class="metric-pill"><div class="metric-value" style="background:linear-gradient(to bottom, #10B981, #059669); -webkit-background-clip:text;">{score}%</div><div class="metric-label">Ready</div></div>
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
        st.plotly_chart(_plotly_layout(fig, height=max(300, len(df)*45)), width="stretch")
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
        st.plotly_chart(_plotly_layout(fig, height=400), width="stretch")
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
        st.plotly_chart(_plotly_layout(fig, height=max(200, len(rows)*40 + 80)), width="stretch")

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
                st.markdown(f'''
                    <div class="skill-header">
                        <div>
                            <div style="font-size:12px; font-weight:900; color:{C_ACCENT}; text-transform:uppercase; letter-spacing:0.3em; margin-bottom:0.5rem;">COGNITIVE NODE</div>
                            <div style="font-size:64px; font-weight:800; color:white; line-height:1; letter-spacing:-0.02em;">{sp_name}</div>
                            <div style="display:flex; gap:12px; margin-top:2rem;">{adj_html}</div>
                        </div>
                        <div style="text-align:right;">
                            <div class="badge badge-{sp.category.lower()}">{sp.category}</div>
                            <div style="font-size:32px; font-weight:800; color:white; margin-top:1.5rem;">{sp.total_weeks} <span style="font-size:14px; color:{C_MUTED}; letter-spacing:0.1em;">WEEKS</span></div>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
                
                # --- NEW FEEDBACK SECTION ---
                feedback = getattr(sp, 'candidate_feedback', "")
                if feedback:
                    st.markdown(f'''
                        <div style="background: linear-gradient(to right, rgba(124, 106, 247, 0.05), transparent); border-left: 4px solid {C_ACCENT}; border-radius: 0 20px 20px 0; padding: 2.5rem; margin-bottom: 3rem;">
                            <div style="font-size: 13px; font-weight: 900; color: {C_ACCENT}; text-transform: uppercase; letter-spacing: 0.2em; margin-bottom: 1rem; display: flex; align-items: center; gap: 10px;">
                                <span style="font-size: 20px;">◈</span> PERSONALIZED FEEDBACK
                            </div>
                            <div style="font-size: 18px; line-height: 1.7; color: {C_TEXT}; font-style: italic; font-weight: 500;">
                                "{html.escape(feedback)}"
                            </div>
                        </div>
                    ''', unsafe_allow_html=True)
                # ----------------------------

                if sp.category == "STRONG":
                    st.markdown(f'<div style="background:rgba(16,185,129,0.05); border:1px solid {C_STRONG}; border-radius:20px; padding:2rem; text-align:center; color:{C_STRONG}; font-weight:700;">MASTERY VERIFIED: No additional roadmap required for this node.</div>', unsafe_allow_html=True)
                    continue
                
                topics = getattr(sp, 'topics', [])
                if not topics:
                    st.markdown(f'''
                        <div style="background:rgba(255,255,255,0.02); border:1px dashed {C_BORDER}; border-radius:24px; padding:4rem; text-align:center; margin-top:2rem;">
                            <div style="font-size:40px; margin-bottom:1rem; opacity:0.5;">◈</div>
                            <div style="font-size:18px; font-weight:700; color:{C_MUTED}; letter-spacing:0.1em; text-transform:uppercase;">
                                Neural Synthesis Pending
                            </div>
                            <div style="font-size:14px; color:{C_MUTED}; margin-top:0.5rem; opacity:0.7;">
                                Deep-dive curriculum for this node is being vectorized...
                            </div>
                        </div>
                    ''', unsafe_allow_html=True)
                    continue

                week_labels = [t.week_label for t in topics]
                st.markdown(f'<div style="font-size:12px; font-weight:800; color:{C_MUTED}; margin-bottom:1rem; letter-spacing:0.1em;">SELECT TIMELINE SEGMENT</div>', unsafe_allow_html=True)
                sel_w = st.radio(f"Select Week for {sp.skill_name}", week_labels, horizontal=True, label_visibility="collapsed", key=f"sel_{sp.skill_name}")
                topic = next((t for t in topics if t.week_label == sel_w), topics[0])
                
                _render_week_content(topic, sp.skill_name)
    except Exception as e: st.error(f"Timeline Error: {e}")

def _render_week_content(topic, skill_id):
    t_title = html.escape(topic.title)
    t_obj = html.escape(topic.objective)
    st.markdown(f'''
        <div style="background: linear-gradient(135deg, rgba(124, 106, 247, 0.1), transparent); border-left: 6px solid {C_ACCENT}; padding: 2.5rem; border-radius: 0 32px 32px 0; margin-bottom: 3rem; box-shadow: 20px 0 40px -20px rgba(124, 106, 247, 0.2);">
            <div style="font-size: 14px; font-weight: 900; color: {C_ACCENT}; text-transform: uppercase; letter-spacing: 0.2em; margin-bottom: 0.5rem;">STRATEGIC OBJECTIVE</div>
            <div style="font-size: 28px; color: white; font-weight: 800; line-height: 1.2;">{t_title}</div>
            <div style="font-size: 18px; color: {C_MUTED}; margin-top: 1rem; line-height: 1.6;">{t_obj}</div>
        </div>
    ''', unsafe_allow_html=True)
    
    with st.expander("📖 CURRICULUM SYLLABUS", expanded=True):
        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
        for i, item in enumerate(topic.what_to_study): 
            st.markdown(f'''
                <div style="display: flex; align-items: flex-start; gap: 15px; margin-bottom: 12px;">
                    <div style="color: {C_ACCENT}; font-weight: 900;">0{i+1}</div>
                    <div style="font-size: 16px; color: {C_TEXT};">{html.escape(item)}</div>
                </div>
            ''', unsafe_allow_html=True)

    st.markdown('<div style="height:3rem;"></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")
    with col1:
        docs_html = "".join([f"<div style='margin-bottom:30px;'><a href='{html.escape(d.url)}' target='_blank' style='color:white; font-weight:800; text-decoration:none; font-size:20px; border-bottom: 1px solid rgba(255,255,255,0.1);'>{html.escape(d.title)}</a><div style='font-size:16px; color:{C_MUTED}; margin-top:8px; line-height:1.6;'>{html.escape(d.description)}</div></div>" for d in topic.documentation])
        st.markdown(f'<div class="res-box"><div class="res-box-title">Official Documentation</div>{docs_html}</div>', unsafe_allow_html=True)
        st.markdown('<div style="height:2rem;"></div>', unsafe_allow_html=True)
        assets_html = "".join([f"<div style='margin-bottom:15px; padding: 16px; background: rgba(255, 255, 255, 0.03); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);'><span class='badge' style='background:rgba(124, 106, 247, 0.1); color:{C_ACCENT}; font-size:11px; padding:6px 12px; margin-right:15px; border: 1px solid rgba(124,106,247,0.2);'>{html.escape(r.type).upper()}</span> <a href='{html.escape(r.url)}' target='_blank' style='color:white; font-weight:700; text-decoration:none; font-size:17px;'>{html.escape(r.title)}</a></div>" for r in topic.extra_resources])
        st.markdown(f'<div class="res-box"><div class="res-box-title">Neural Deep Dives</div>{assets_html}</div>', unsafe_allow_html=True)
    with col2:
        yt = topic.youtube
        st.markdown(f"""
        <div class="res-box" style="border-top: 4px solid {C_GAP}; background: linear-gradient(to bottom, rgba(244, 63, 94, 0.05), transparent);">
            <div class="res-box-title" style="color: {C_GAP} !important;">🔥 Visual Training (3 Levels)</div>
            <div class="yt-level-card">
                <div style="font-size:12px; font-weight:900; color:{C_STRONG}; margin-bottom:8px; letter-spacing:0.1em;">PHASE 01: CONCEPTUAL</div>
                <a href="{html.escape(yt.easy.url)}" target="_blank" class="yt-title">{html.escape(yt.easy.title)}</a>
                <div style="font-size:14px; color:{C_MUTED};">📺 {html.escape(yt.easy.channel)} • <span style="color:{C_STRONG}; font-weight:800;">{html.escape(yt.easy.why)}</span></div>
            </div>
            <div class="yt-level-card">
                <div style="font-size:12px; font-weight:900; color:{C_DEVELOPING}; margin-bottom:8px; letter-spacing:0.1em;">PHASE 02: ARCHITECTURAL</div>
                <a href="{html.escape(yt.medium.url)}" target="_blank" class="yt-title">{html.escape(yt.medium.title)}</a>
                <div style="font-size:14px; color:{C_MUTED};">📺 {html.escape(yt.medium.channel)} • <span style="color:{C_DEVELOPING}; font-weight:800;">{html.escape(yt.medium.why)}</span></div>
            </div>
            <div class="yt-level-card">
                <div style="font-size:12px; font-weight:900; color:{C_GAP}; margin-bottom:8px; letter-spacing:0.1em;">PHASE 03: INTERNAL DEEP DIVE</div>
                <a href="{html.escape(yt.hard.url)}" target="_blank" class="yt-title">{html.escape(yt.hard.title)}</a>
                <div style="font-size:14px; color:{C_MUTED};">📺 {html.escape(yt.hard.channel)} • <span style="color:{C_GAP}; font-weight:800;">{html.escape(yt.hard.why)}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div style="height:2rem;"></div>', unsafe_allow_html=True)
        t_ho = html.escape(topic.hands_on)
        t_ms = html.escape(topic.milestone)
        st.markdown(f'<div class="res-box"><div class="res-box-title">Tactical Project</div><div style="font-size:18px; font-weight:800; color:white; margin-bottom:15px; line-height:1.4;">{t_ho}</div><div style="background:rgba(16,185,129,0.05); border:1px solid {C_STRONG}; border-radius:16px; padding:20px;"><div style="color:{C_STRONG}; font-size:12px; font-weight:900; margin-bottom:8px; letter-spacing:0.1em;">COMPLETION MILESTONE</div><div style="font-size:15px; color:white; line-height:1.5;">{t_ms}</div></div></div>', unsafe_allow_html=True)

def _block7_readiness(plan: LearningPlan):
    try:
        st.markdown('<div class="section-title">Readiness Pulse</div>', unsafe_allow_html=True)
        score = getattr(plan, 'readiness_score', 0)
        fig = go.Figure(go.Indicator(mode="gauge+number", value=score, number={'suffix': "%", 'font': {'size': 80, 'color': 'white', 'family': 'JetBrains Mono'}}, gauge={'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "rgba(255,255,255,0.1)"}, 'bar': {'color': C_STRONG if score > 70 else C_DEVELOPING if score > 40 else C_GAP, 'thickness': 1}, 'bgcolor': "rgba(255,255,255,0.01)", 'steps': [{'range': [0, 100], 'color': 'rgba(255,255,255,0.02)'}]}))
        st.plotly_chart(_plotly_layout(fig, height=300), width="stretch")
    except Exception as e: st.error(f"Readiness Error: {e}")

def _block8_motivation(plan: LearningPlan):
    try:
        st.markdown('<div class="section-title">Intelligence Synthesis</div>', unsafe_allow_html=True)
        summary = html.escape(getattr(plan, 'summary', 'Processing complete.'))
        st.markdown(f'<div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(2, 6, 23, 1)); border: 1px solid {C_BORDER}; border-radius: 32px; padding: 4rem; line-height: 2; font-size: 20px; color: #E2E8F0; box-shadow: 0 40px 80px -20px rgba(0,0,0,0.5);">{summary}</div>', unsafe_allow_html=True)
    except Exception as e: st.error(f"Motivation Error: {e}")
