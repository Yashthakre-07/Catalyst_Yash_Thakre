CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
  --accent: #7C6AF7;
  --accent-glow: rgba(124, 106, 247, 0.4);
  --accent-light: #A78BFA;
  --violet: #8B5CF6;
  --emerald: #10B981;
  --bg: #020617;
  --bg-card: rgba(10, 15, 30, 0.6);
  --text: #FFFFFF;
  --text-muted: #94A3B8;
  --border: rgba(255, 255, 255, 0.08);
}

* { box-sizing: border-box; margin: 0; padding: 0; }

/* GOD TIER SCROLLBAR */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: linear-gradient(var(--accent), var(--emerald)); border-radius: 10px; }

html, body, [class*="css"], .stApp {
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-size: 20px !important;
  background-color: var(--bg) !important;
  color: var(--text) !important;
  overflow-x: hidden !important;
}

/* GOD LEVEL MOVING MESH BACKGROUND */
.stApp { background: var(--bg) !important; }
.stApp::before {
  content: ""; position: fixed; top: -50%; left: -50%; width: 200%; height: 200%;
  background: 
    radial-gradient(circle at 20% 20%, rgba(124, 106, 247, 0.12) 0%, transparent 40%),
    radial-gradient(circle at 80% 80%, rgba(16, 185, 129, 0.08) 0%, transparent 40%),
    radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.04) 0%, transparent 50%);
  animation: meshFlow 30s infinite alternate linear; pointer-events: none; z-index: 0;
}
@keyframes meshFlow { 0% { transform: rotate(0deg) scale(1); } 100% { transform: rotate(15deg) scale(1.1); } }

/* NEURAL GRID */
.stApp::after {
  content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background-image: linear-gradient(rgba(255, 255, 255, 0.015) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.015) 1px, transparent 1px);
  background-size: 80px 80px; pointer-events: none; z-index: 1;
}

/* PROGRESS BAR - CINEMATIC */
.nav-container { width: 100%; max-width: 600px; margin: 2rem auto; padding: 1rem 0; position: relative; z-index: 1000; }
.nav-track-bg { position: absolute; top: 32px; left: 0; width: 100%; height: 2px; background: rgba(255, 255, 255, 0.05); z-index: 1; }
.nav-nodes { display: flex; justify-content: space-between; align-items: center; position: relative; z-index: 2; }
.nav-node { 
    width: 44px; height: 44px; border-radius: 16px; background: #0F172A; 
    border: 1px solid rgba(255, 255, 255, 0.1); display: flex; align-items: center; justify-content: center; 
    font-weight: 800; font-size: 16px; color: #475569; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.nav-node.active { border-color: var(--accent); color: white; box-shadow: 0 0 30px var(--accent-glow); transform: scale(1.2) rotate(5deg); }
.nav-node.complete { background: var(--accent); border-color: var(--accent); color: white; }
.nav-label { font-size: 13px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.2em; color: #475569; margin-top: 10px; }
.nav-label.active { color: var(--accent-light); text-shadow: 0 0 10px var(--accent-glow); }

/* HERO - BREATHTAKING */
.hero-title-god { font-size: 140px !important; font-weight: 800 !important; line-height: 0.85 !important; letter-spacing: -0.05em !important; margin-bottom: 2rem; color: #FFFFFF; }
.hero-title-god span { 
    background: linear-gradient(135deg, #FFF 0%, #A78BFA 50%, #10B981 100%); 
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
    filter: drop-shadow(0 0 30px rgba(124, 106, 247, 0.4));
}

/* GOD LEVEL GLASS CARD */
div[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--bg-card) !important; backdrop-filter: blur(80px) !important; -webkit-backdrop-filter: blur(80px) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important; border-radius: 40px !important; padding: 4rem !important;
  max-width: 600px !important; margin: 0 auto !important; box-shadow: 0 50px 150px -30px rgba(0, 0, 0, 0.9) !important;
  animation: godEntrance 1s cubic-bezier(0.16, 1, 0.3, 1); position: relative; overflow: hidden !important;
}
@keyframes godEntrance { from { opacity: 0; transform: scale(0.95) translateY(60px); } to { opacity: 1; transform: scale(1) translateY(0); } }

/* BUTTONS - PULSING NEON */
.stButton > button {
  background: linear-gradient(135deg, #7C6AF7 0%, #8B5CF6 100%) !important; 
  color: white !important; border-radius: 20px !important;
  padding: 1.5rem 3rem !important; font-size: 20px !important; font-weight: 800 !important; 
  box-shadow: 0 20px 40px -10px var(--accent-glow) !important;
  width: 100% !important; border: none !important; text-transform: uppercase; letter-spacing: 0.1em;
  transition: all 0.3s ease !important;
}
.stButton > button:hover {
  transform: translateY(-5px) !important;
  box-shadow: 0 30px 60px -10px var(--accent-glow) !important;
  filter: brightness(1.1);
}

.section-title-best { font-size: 48px !important; font-weight: 800 !important; letter-spacing: -0.03em !important; margin-bottom: 1.5rem; color: #FFFFFF; }

/* ULTRA GOD LEVEL PROCESSING (SVG GEARS) */
.neural-core-container { display: flex; flex-direction: column; align-items: center; justify-content: center; padding-top: 6rem; position: relative; }
.gear-wrapper { position: relative; width: 200px; height: 160px; display: flex; justify-content: center; align-items: center; }
.gear { position: absolute; filter: drop-shadow(0 0 15px rgba(124, 106, 247, 0.5)); }
.gear-large { 
  width: 100px; height: 100px; left: 20px; top: 40px; 
  animation: spinGear 4s linear infinite; 
}
.gear-small { 
  width: 70px; height: 70px; right: 30px; top: 10px; 
  animation: spinGearReverse 2.8s linear infinite; 
}
.core-glow {
  position: absolute; width: 120px; height: 120px; border-radius: 50%;
  background: radial-gradient(circle, rgba(124, 106, 247, 0.4) 0%, transparent 70%);
  top: 20px; left: 40px; animation: pulseGlow 2s ease-in-out infinite alternate; z-index: -1;
}

@keyframes spinGear { to { transform: rotate(360deg); } }
@keyframes spinGearReverse { to { transform: rotate(-360deg); } }
@keyframes pulseGlow { from { transform: scale(0.8); opacity: 0.5; } to { transform: scale(1.2); opacity: 1; } }

.fascinating-text {
  font-size: 34px; font-weight: 800; margin-top: 2rem;
  background: linear-gradient(to right, #A78BFA, #10B981);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  animation: shimmerGod 2.5s infinite; letter-spacing: -0.01em;
}

/* SHIMMER ANIMATION */
@keyframes shimmerGod { 0%, 100% { opacity: 0.6; transform: scale(0.98); } 50% { opacity: 1; transform: scale(1); } }

/* CHAT CONTAINER */
div[data-testid="stChatMessageContainer"] { padding: 0.75rem !important; }
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"][data-testid] { max-width: 100% !important; }

/* BUTTONS & INPUTS */
.stButton > button {
  background: linear-gradient(135deg, #7C6AF7 0%, #6366F1 100%) !important; color: white !important; border-radius: 12px !important;
  padding: 1rem 2.5rem !important; font-size: 18px !important; font-weight: 800 !important; box-shadow: 0 10px 25px -5px rgba(124, 106, 247, 0.4) !important;
  width: 100% !important; border: none !important; text-transform: uppercase; letter-spacing: 0.05em;
}
.stTextArea textarea { background: rgba(0,0,0,0.5) !important; border: 1px solid rgba(255,255,255,0.05) !important; border-radius: 12px !important; font-size: 16px !important; }

header, footer { display: none !important; }
.block-container { padding: 0 1rem !important; }

/* ═══ RESULTS PAGE ═══ */
.report-header {
  text-align: center; padding: 2rem 0 1.5rem; 
  border-bottom: 1px solid var(--border); margin-bottom: 2rem;
}
.report-name { font-size: 64px; font-weight: 800; letter-spacing: -0.03em; }
.report-role { 
  color: var(--emerald); font-weight: 700; font-family: 'JetBrains Mono', monospace;
  text-transform: uppercase; letter-spacing: 0.15em; font-size: 18px; margin-top: 0.5rem;
}
.report-meta {
  display: flex; justify-content: center; gap: 2rem; margin-top: 1rem;
  font-size: 16px; color: var(--text-muted); font-family: 'JetBrains Mono', monospace;
}
.report-meta span { display: flex; align-items: center; gap: 6px; }

/* Summary Box */
.summary-box {
  background: rgba(124, 106, 247, 0.05); border: 1px solid rgba(124, 106, 247, 0.15);
  border-radius: 16px; padding: 1.5rem; margin-bottom: 2rem; font-size: 18px;
  line-height: 1.7; color: var(--text-muted);
}

/* Skill Card */
.skill-card {
  background: rgba(15, 23, 42, 0.5); backdrop-filter: blur(20px);
  border: 1px solid var(--border); border-radius: 20px; padding: 1.5rem; margin-bottom: 1rem;
}
.skill-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.skill-card-name { font-size: 26px; font-weight: 800; }
.badge { 
  padding: 4px 12px; border-radius: 100px; font-size: 14px; font-weight: 800;
  text-transform: uppercase; letter-spacing: 0.1em;
}
.badge-strong { background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); }
.badge-developing { background: rgba(251, 191, 36, 0.15); color: #FBBF24; border: 1px solid rgba(251, 191, 36, 0.3); }
.badge-gap { background: rgba(239, 68, 68, 0.15); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.3); }

/* Level Bar */
.level-bar-container { display: flex; align-items: center; gap: 12px; margin-bottom: 0.75rem; }
.level-label { font-size: 14px; color: var(--text-muted); width: 100px; font-weight: 600; }
.level-track { flex: 1; height: 12px; background: rgba(255,255,255,0.05); border-radius: 100px; overflow: hidden; }
.level-fill { height: 100%; border-radius: 100px; transition: width 1.5s cubic-bezier(0.34, 1.56, 0.64, 1); }
.level-fill-accent { background: linear-gradient(90deg, var(--accent), var(--accent-light)); }
.level-fill-emerald { background: linear-gradient(90deg, var(--emerald), #34D399); }
.level-value { font-size: 16px; font-weight: 800; font-family: 'JetBrains Mono', monospace; width: 40px; }

/* Reasoning */
.reasoning { font-size: 16px; color: var(--text-muted); line-height: 1.6; margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid var(--border); }

/* Resource Card */
.res-card {
  display: inline-flex; align-items: center; gap: 8px; padding: 8px 18px;
  background: rgba(124, 106, 247, 0.06); border: 1px solid rgba(124, 106, 247, 0.12);
  border-radius: 10px; font-size: 16px; color: var(--accent-light); margin: 4px 4px 4px 0;
}
.res-type { font-size: 12px; font-weight: 800; text-transform: uppercase; color: var(--text-muted); }

/* Weekly Breakdown */
.week-item {
  display: flex; align-items: flex-start; gap: 12px; padding: 0.5rem 0;
  font-size: 16px; color: var(--text-muted);
}
.week-dot { 
  width: 8px; height: 8px; border-radius: 50%; background: var(--accent); margin-top: 5px; flex-shrink: 0;
  box-shadow: 0 0 8px var(--accent);
}

/* Strengths */
.strength-pill {
  display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px;
  background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 100px; font-size: 16px; font-weight: 700; color: #34D399; margin: 4px;
}

/* Section Divider */
.section-div { 
  font-size: 20px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.15em;
  color: var(--accent-light); margin: 2rem 0 1rem; padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border);
}
</style>
"""

ORBS = """
<div style="position:fixed; width:500px; height:500px; background:radial-gradient(circle, #7C6AF7 0%, transparent 70%); opacity:0.1; top:-150px; left:-150px; pointer-events:none; z-index:0;"></div>
<div style="position:fixed; width:400px; height:400px; background:radial-gradient(circle, #10B981 0%, transparent 70%); opacity:0.06; bottom:-150px; right:-150px; pointer-events:none; z-index:0;"></div>
"""
