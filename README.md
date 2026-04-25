<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/Gemini_Flash-AI-8B5CF6?style=for-the-badge&logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/Groq_Llama_3.3-AI-F97316?style=for-the-badge&logo=meta&logoColor=white" />
  <img src="https://img.shields.io/badge/Pydantic-V2-E92063?style=for-the-badge&logo=pydantic&logoColor=white" />
</p>

<h1 align="center">◈ NeuralHire</h1>
<h3 align="center">Autonomous AI Skill Assessment & Personalized Learning Plan Agent</h3>

<p align="center">
  <i>A production-grade, multi-provider AI system that conducts real-time technical interviews, identifies skill gaps, scores proficiency, and generates cinematic, week-by-week learning roadmaps — all through a stunning Neural Dark UI.</i>
</p>

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Live Demo](#-live-demo)
- [Architecture & How It Works](#-architecture--how-it-works)
- [4-Phase Pipeline (Deep Dive)](#-4-phase-pipeline-deep-dive)
- [Project Structure](#-project-structure)
- [File-by-File Breakdown](#-file-by-file-breakdown)
- [Data Models (Pydantic Schemas)](#-data-models-pydantic-schemas)
- [AI Engine & Multi-Key Rotation](#-ai-engine--multi-key-rotation)
- [The Neural Dark UI](#-the-neural-dark-ui)
- [PDF Export Engine](#-pdf-export-engine)
- [Tech Stack](#-tech-stack)
- [Installation & Setup](#-installation--setup)
- [Environment Variables](#-environment-variables)
- [Usage Guide](#-usage-guide)
- [Deployment (Streamlit Cloud)](#-deployment-streamlit-cloud)
- [Security](#-security)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🧠 Overview

**NeuralHire** is not a simple quiz app. It is a **fully autonomous AI agent** that:

1. **Reads** a Job Description and a Candidate Resume.
2. **Extracts** the required skills from the JD and the candidate's profile from the resume — using AI.
3. **Conducts a live, adaptive technical interview** — asking 3 targeted questions per skill, adjusting based on the candidate's answers in real-time.
4. **Scores** each skill on a 1–10 scale with detailed reasoning, categorizing them as `STRONG`, `DEVELOPING`, or `GAP`.
5. **Generates a personalized, week-by-week learning plan** with curated YouTube videos (Easy/Medium/Hard), official documentation, hands-on projects, and milestones.
6. **Exports everything** as a high-fidelity, dark-themed PDF report.

The entire experience is wrapped in a **cinematic "Neural Dark" UI** with glassmorphism, animated orbs, pulsating glows, and a hacker-aesthetic design language.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| **AI-Powered Document Parsing** | Extracts structured data from raw resume and JD text using LLMs |
| **Autonomous Technical Screening** | Conducts a 3-question-per-skill adaptive interview without human intervention |
| **Intelligent Skill Scoring** | Scores proficiency (1-10) with gap analysis and priority weighting |
| **Personalized Learning Roadmap** | Generates week-by-week study plans with curated resources |
| **Multi-Provider AI Engine** | Supports both Google Gemini and Groq (Llama 3.3) with automatic failover |
| **10-Key Rotation System** | Rotates through up to 10 API keys to avoid rate limits |
| **Neural Dark UI** | Cinematic, premium dark-mode interface with animations and glassmorphism |
| **PDF Export** | Generates a high-fidelity dark-themed PDF matching the web dashboard |
| **Robust Fallbacks** | Every AI call has a graceful fallback to prevent crashes |

---

## 🎬 Live Demo

> Deploy your own instance on Streamlit Cloud in under 2 minutes. See [Deployment](#-deployment-streamlit-cloud).

---

## 🏗 Architecture & How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                        STREAMLIT UI (main.py)                   │
│  Hero → JD Upload → Resume Upload → Assessment Chat → Results  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  AssessmentAgent │  ← Central Orchestrator
                    │   (agent/core)  │
                    └──┬───┬───┬───┬──┘
                       │   │   │   │
              ┌────────┘   │   │   └────────┐
              ▼            ▼   ▼            ▼
        ┌──────────┐ ┌────────┐ ┌───────┐ ┌─────────┐
        │  Parsers │ │Assessor│ │Scorer │ │ Planner │
        │ (resume, │ │  (Q&A) │ │(1-10) │ │(roadmap)│
        │   jd)    │ │        │ │       │ │         │
        └────┬─────┘ └───┬────┘ └───┬───┘ └────┬────┘
             │            │         │           │
             └────────────┼─────────┼───────────┘
                          ▼         ▼
                    ┌─────────────────────┐
                    │     AIClient        │
                    │  (Multi-Key Rotation│
                    │   Gemini + Groq)    │
                    └─────────────────────┘
```

### Flow Summary

1. **User** uploads a Job Description and Resume via the Streamlit UI.
2. **`AssessmentAgent`** (the central orchestrator) calls the **Parsers** to extract structured data.
3. For each extracted skill, the **Assessor** generates adaptive interview questions.
4. After the conversation, the **Scorer** evaluates the candidate's proficiency.
5. Finally, the **Planner** generates a personalized learning roadmap.
6. The **Results Dashboard** renders everything in a cinematic UI, with an option to **export as PDF**.

---

## 🔬 4-Phase Pipeline (Deep Dive)

### Phase 01: Document Intelligence

**Files:** `parsers/resume_parser.py`, `parsers/jd_parser.py`

The system takes raw text (pasted or extracted from PDF) and uses the LLM to extract structured JSON:

- **Resume → `CandidateProfile`**: Extracts `name`, `current_role`, `years_experience`, and `skills_from_resume`.
- **JD → Skill List**: Extracts an array of skills, each with `skill_name`, `required_level` (1-10), `is_required` (bool), and `context` (why the JD needs it).

**Fallback Logic:** If the AI fails to parse, the JD parser falls back to keyword matching against common skills (Python, SQL, Docker, etc.).

---

### Phase 02: Autonomous Technical Screening

**File:** `agent/assessor.py`

For each skill extracted from the JD, the system conducts a **3-question adaptive interview**:

1. The LLM receives the candidate's background + conversation history.
2. It generates a contextual question.
3. The candidate answers via the chat interface.
4. The LLM sees the full transcript and asks the next question.
5. After 3 questions, it signals `"type": "complete"`.

**Safeguards:**
- If the LLM tries to end early (before 3 questions), the system **forces** a follow-up question.
- If the LLM response is unparseable, a **generic fallback question** is injected.
- A configurable `MAX_QUESTIONS_PER_SKILL` (default: 3) acts as a hard cap.

---

### Phase 03: Intelligent Scoring

**File:** `agent/scorer.py`

After the conversation for each skill, the scorer:

1. Sends the full Q&A transcript to the LLM.
2. The LLM scores the candidate from **1 to 10**.
3. Calculates `gap_score = required_level - assessed_level`.
4. Assigns a category:
   - **STRONG** (≥8): Candidate exceeds or meets the bar.
   - **DEVELOPING** (5-7): Candidate has foundational knowledge.
   - **GAP** (≤4): Significant skill deficit.
5. Calculates a **priority_score** using the formula:
   ```
   priority_score = (gap_score × 0.6) + (criticality × 0.4)
   ```
   Where `criticality = 10` if the skill is required, `5` if nice-to-have.

**Fallback:** If scoring fails, returns a safe default (`assessed_level=1`, `category="GAP"`).

---

### Phase 04: Learning Plan Generation

**File:** `agent/planner.py`

The planner synthesizes everything into a **personalized, week-by-week curriculum**:

- **GAP skills** → 4 weeks of intensive study.
- **DEVELOPING skills** → 2 weeks of targeted improvement.
- **STRONG skills** → 0 weeks (no study needed).

Each week includes:
| Field | Description |
|---|---|
| `title` | Topic name for the week |
| `objective` | What the candidate will achieve |
| `what_to_study` | Bullet list of concepts |
| `youtube.easy/medium/hard` | 3-tier curated YouTube videos |
| `documentation` | Official docs and articles |
| `hands_on` | A practical project or exercise |
| `milestone` | Success criteria for the week |

---

## 📁 Project Structure

```
skill-assessment-agent/
│
├── main.py                    # Streamlit entry point — the entire UI flow
├── results_dashboard.py       # Cinematic results rendering (charts, tables, resources)
├── ui_styles.py               # Global CSS — Neural Dark theme, animations, glassmorphism
├── pdf_generator.py           # Standalone PDF generator (legacy)
├── requirements.txt           # Python dependencies
├── .env                       # API keys (NEVER committed to Git)
├── .env.example               # Template for .env setup
├── .gitignore                 # Protects .env and __pycache__
├── README.md                  # This file
├── GUIDELINES.md              # Internal development guidelines
│
├── agent/                     # 🧠 The AI Brain
│   ├── __init__.py
│   ├── core.py                # AssessmentAgent — the central orchestrator
│   ├── assessor.py            # Generates adaptive interview questions
│   ├── scorer.py              # Scores skill proficiency (1-10)
│   ├── planner.py             # Generates the personalized learning plan
│   ├── prompts.py             # All LLM prompt templates
│   ├── test_assess.py         # Unit test for assessor
│   └── test_plan.py           # Unit test for planner
│
├── config/                    # ⚙️ Configuration
│   ├── __init__.py
│   └── settings.py            # Loads .env variables into Python constants
│
├── data/                      # 📄 Sample Data
│   ├── sample_jd.txt          # Example Job Description
│   └── sample_resume.txt      # Example Resume
│
├── models/                    # 📐 Pydantic Data Models
│   ├── __init__.py
│   ├── candidate.py           # CandidateProfile schema
│   ├── skill.py               # SkillAssessment schema
│   └── learning_plan.py       # LearningPlan, SkillPlan, WeeklyTopic schemas
│
├── parsers/                   # 🔍 Document Parsers
│   ├── __init__.py
│   ├── resume_parser.py       # AI-powered resume extraction
│   ├── jd_parser.py           # AI-powered JD skill extraction
│   └── test_parse.py          # Unit test for parsers
│
└── utils/                     # 🔧 Utilities
    ├── __init__.py
    ├── ai_client.py           # Multi-provider AI wrapper (Gemini + Groq)
    ├── file_handler.py        # PDF text extraction & JSON saving
    ├── logger.py              # Loguru logging configuration
    ├── pdf_generator.py       # Neural Dark PDF report generator
    └── resource_finder.py     # Skill resource lookup engine
```

---

## 📄 File-by-File Breakdown

### `main.py` — The Command Center
The Streamlit entry point that orchestrates the entire user experience across **5 phases**:

| Phase | Name | What Happens |
|---|---|---|
| `hero` | Landing Page | Displays the cinematic "NeuralHire" hero with animated orbs |
| `step_jd` | JD Upload | User pastes or uploads a Job Description |
| `step_resume` | Resume Upload | User pastes or uploads their Resume |
| `assessing` | Live Interview | Real-time chat with the AI agent, skill by skill |
| `results` | Intelligence Dashboard | Full results with charts, resources, and PDF download |

### `agent/core.py` — The Orchestrator
The `AssessmentAgent` class is the **brain** of the system. It:
- Holds all state (`candidate_profile`, `required_skills`, `conversation_history`, `skill_assessments`)
- Coordinates calls between parsers, assessor, scorer, and planner
- Manages the `current_skill_index` to track progress through skills

### `agent/assessor.py` — The Interviewer
Generates adaptive questions using the LLM. Key behaviors:
- Formats the full conversation history before each call
- Forces at least 3 questions per skill (overrides premature completion)
- Falls back to generic questions if the LLM response fails to parse

### `agent/scorer.py` — The Evaluator
Scores each skill after the conversation:
- Sends the full Q&A transcript to the LLM for analysis
- Enforces strict category assignments (`STRONG ≥ 8`, `DEVELOPING 5-7`, `GAP ≤ 4`)
- Calculates a priority score for ordering in the learning plan

### `agent/planner.py` — The Curriculum Designer
Generates the final learning roadmap:
- Queries the `resource_finder` for curated resources
- Sends all data (profile + assessments + resources) to the LLM
- Validates the response against the `LearningPlan` Pydantic schema
- Falls back to a skeletal plan if the LLM response is invalid

### `agent/prompts.py` — The Prompt Library
Contains all 5 prompt templates used across the system:
1. `SKILL_EXTRACTOR_PROMPT` — JD → skill list
2. `RESUME_PARSER_PROMPT` — Resume → candidate profile
3. `ASSESSOR_PROMPT` — Conversation → next question
4. `SCORER_PROMPT` — Transcript → skill score
5. `PLANNER_PROMPT` — Assessments → learning plan

### `utils/ai_client.py` — The AI Engine
The most critical utility. Features:
- **Auto-discovery**: Scans `.env` for up to 10 keys per provider (`GEMINI_API_KEY`, `GEMINI_API_KEY1`, ..., `GEMINI_API_KEY9`)
- **Global rotation**: A static `_global_rotation_idx` ensures keys rotate across all instances
- **Failover**: If Groq fails, automatically tries Gemini keys (and vice versa)
- **Rate limit handling**: Detects 429 errors and applies a 3s backoff before rotating
- **JSON extraction**: Strips markdown fences and extracts valid JSON from LLM responses
- **Cooldown**: After all keys fail one cycle, applies a 5s cooldown before retrying

### `utils/file_handler.py` — File I/O
- `extract_text_from_pdf()` — Uses PyMuPDF to extract raw text from uploaded PDFs
- `save_json_to_file()` — Saves dictionaries as formatted JSON in the `outputs/` directory

### `utils/pdf_generator.py` — The PDF Engine
Generates a **Neural Dark themed PDF** using ReportLab:
- Custom page painting with dark backgrounds and accent lines
- Decorative grid patterns and randomized "neural node" diagrams
- Color-coded skill assessment tables
- Structured curriculum pages with resource grids

### `results_dashboard.py` — The Visual Layer
Renders the final assessment results with:
- Animated metric cards (readiness score, skill count, timeline)
- Color-coded skill gap tables
- Interactive YouTube resource grids with Easy/Medium/Hard levels
- Pulsating glow effects and hover animations
- Official documentation links and hands-on project cards

### `ui_styles.py` — The Design System
Contains all CSS for the Neural Dark theme:
- Global color palette (deep navy, neural purple, emerald, crimson)
- Glassmorphism card effects with `backdrop-filter: blur()`
- Animated floating orbs background
- Typography system with Google Fonts
- Navigation step indicator with animated progress bar

### `config/settings.py` — Configuration Loader
Loads all environment variables using `python-dotenv`:
- `AI_PROVIDER` — Primary AI provider ("gemini" or "groq")
- `GEMINI_MODEL` — Model name (default: `gemini-flash-latest`)
- `GROQ_MODEL` — Model name (default: `llama-3.3-70b-versatile`)
- `MAX_QUESTIONS_PER_SKILL` — Questions per skill (default: 3)

---

## 📐 Data Models (Pydantic Schemas)

All data flowing through the system is validated by **Pydantic V2** schemas:

### `CandidateProfile`
```python
class CandidateProfile(BaseModel):
    name: str                       # "Yash Thakre"
    current_role: str               # "Software Engineer"
    years_experience: int           # 3
    skills_from_resume: list[str]   # ["Python", "React", "SQL"]
    resume_text: str                # Raw resume text
```

### `SkillAssessment`
```python
class SkillAssessment(BaseModel):
    skill_name: str                                    # "Python"
    required_level: int                                # 8
    claimed_level: int                                 # 5
    assessed_level: int                                # 6
    gap_score: int                                     # 2
    priority_score: float                              # 5.2
    category: Literal["STRONG", "DEVELOPING", "GAP"]   # "DEVELOPING"
    assessment_reasoning: str                          # "Candidate showed..."
```

### `LearningPlan`
```python
class LearningPlan(BaseModel):
    candidate_name: str         # "Yash Thakre"
    target_role: str            # "Backend Engineer"
    total_weeks: int            # 12
    readiness_score: int        # 65
    summary: str                # "Executive summary..."
    skills: List[SkillPlan]     # Per-skill breakdown
```

### `WeeklyTopic`
```python
class WeeklyTopic(BaseModel):
    week_label: str             # "Week 1"
    title: str                  # "Python Fundamentals"
    objective: str              # "Master core syntax..."
    what_to_study: List[str]    # ["Variables", "Functions", ...]
    documentation: List[Resource]
    youtube: YoutubeResources   # easy, medium, hard
    extra_resources: List[Resource]
    hands_on: str               # "Build a CLI tool..."
    milestone: str              # "Complete 5 exercises..."
```

---

## 🔄 AI Engine & Multi-Key Rotation

The `AIClient` class is the heart of the system's reliability:

```
┌──────────────────────────────────────────────────────┐
│                     AIClient                         │
│                                                      │
│  Key Pool:                                           │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐               │
│  │ GROQ_1  │ │ GROQ_2  │ │ GROQ_3  │  ← Priority 1 │
│  └─────────┘ └─────────┘ └─────────┘               │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │GEMINI_0 │ │GEMINI_1 │ │GEMINI_2 │ │GEMINI_3 │   │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘   │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐               │
│  │GEMINI_4 │ │GEMINI_5 │ │GEMINI_6 │  ← Priority 2 │
│  └─────────┘ └─────────┘ └─────────┘               │
│                                                      │
│  Rotation: Global static index across all instances  │
│  Failover: Auto-skip on 429/quota/error              │
│  Cooldown: 5s after full cycle, 3s on rate limit     │
└──────────────────────────────────────────────────────┘
```

### How It Works:
1. **Discovery**: On init, scans `.env` for `GEMINI_API_KEY`, `GEMINI_API_KEY1`, ..., `GEMINI_API_KEY9` (same for Groq).
2. **Ordering**: Groq keys are tried first (faster inference), then Gemini.
3. **Rotation**: A `_global_rotation_idx` (static class variable) ensures rotation persists across all `AIClient` instances.
4. **Error Handling**: On any failure (429, quota, network), the index advances to the next key.
5. **Cooldown**: After cycling through all keys once, a 5s cooldown is applied before the next pass.
6. **Max Retries**: Default 10 attempts before raising `RuntimeError`.

---

## 🎨 The Neural Dark UI

The interface is designed to feel like a **next-generation AI command center**:

- **Hero Page**: Full-screen animated landing with floating gradient orbs and glowing "Neural Sync Active" badge.
- **Step Navigation**: A 4-step progress bar with animated fill and node indicators (Requirement → Candidate → Assessment → Intelligence).
- **Assessment Chat**: Real-time conversational interface with skill progress tracking.
- **Results Dashboard**: Cinematic display of assessment results with:
  - Glassmorphism cards with `backdrop-filter: blur(20px)`
  - Pulsating glow animations on resource boxes
  - Color-coded skill tables (Green/Amber/Red)
  - Interactive YouTube cards with hover-scale effects
  - Emoji-enhanced difficulty labels (⚡ Easy, 🚀 Medium, 💀 Hard)

### Color Palette
| Token | Hex | Usage |
|---|---|---|
| `--bg` | `#020617` | Deep space background |
| `--surface` | `#0F172A` | Card backgrounds |
| `--accent` | `#7C6AF7` | Neural Purple (primary) |
| `--emerald` | `#10B981` | Success / Strong |
| `--amber` | `#F59E0B` | Warning / Developing |
| `--crimson` | `#EF4444` | Danger / Gap |
| `--text` | `#F8FAFC` | Primary text |
| `--text-muted` | `#94A3B8` | Secondary text |

---

## 📥 PDF Export Engine

The PDF generator (`utils/pdf_generator.py`) creates a document that mirrors the web dashboard:

- **Dark Canvas**: Every page is painted with `#020617` background
- **Accent Sidebar**: A 5px purple bar runs along the left edge
- **Grid Overlay**: Subtle grid lines create a HUD effect
- **Neural Nodes**: Randomized decorative nodes on the first page
- **Content Sections**:
  - Identity header with candidate name and role
  - Metrics hub (Readiness %, Nodes, Timeline)
  - Executive Summary with accent border
  - Skill Assessment Grid with color-coded statuses
  - Week-by-week curriculum with resource tables

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | Streamlit | Interactive web UI framework |
| **Styling** | Vanilla CSS | Neural Dark theme with glassmorphism |
| **AI (Primary)** | Google Gemini Flash | Fast, free-tier LLM for all AI tasks |
| **AI (Fallback)** | Groq (Llama 3.3 70B) | High-quality fallback provider |
| **Validation** | Pydantic V2 | Type-safe data models with validation |
| **PDF** | ReportLab | Programmatic PDF generation |
| **PDF Parsing** | PyMuPDF (fitz) | Extracting text from uploaded PDFs |
| **Logging** | Loguru | Beautiful, structured logging |
| **Config** | python-dotenv | Environment variable management |

---

## ⚡ Installation & Setup

### Prerequisites
- Python 3.12+
- At least one API key (Gemini or Groq)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/Yashthakre-07/Catalyst_Yash_Thakre.git
cd Catalyst_Yash_Thakre

# 2. Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux

# 5. Edit .env and add your API keys
# See "Environment Variables" section below

# 6. Run the application
streamlit run main.py
```

The app will open at `http://localhost:8501`.

---

## 🔐 Environment Variables

Create a `.env` file in the project root (use `.env.example` as a template):

```env
# Primary AI provider
AI_PROVIDER=gemini

# Google Gemini Keys (add as many as you have)
GEMINI_API_KEY="your-key-here"
GEMINI_API_KEY1="your-second-key"
GEMINI_API_KEY2="your-third-key"
# ... up to GEMINI_API_KEY9

GEMINI_MODEL=gemini-flash-latest

# Groq Keys (add as many as you have)
GROQ_API_KEY1="your-groq-key"
GROQ_API_KEY2="your-second-groq-key"
GROQ_MODEL=llama-3.3-70b-versatile

# App Config
LOG_LEVEL=INFO
MAX_QUESTIONS_PER_SKILL=3
```

> **Tip:** The more API keys you add, the more resilient the system becomes against rate limits. The system auto-discovers and rotates through all keys.

### Getting API Keys
| Provider | Where to Get | Free Tier |
|---|---|---|
| **Google Gemini** | [aistudio.google.com](https://aistudio.google.com) | Yes — 20 requests/day/model |
| **Groq** | [console.groq.com](https://console.groq.com) | Yes — generous rate limits |

---

## 🚀 Usage Guide

1. **Launch** the app with `streamlit run main.py`.
2. **Click "Initiate Scan"** on the hero page.
3. **Paste or upload a Job Description** (Phase 01).
4. **Paste or upload a Resume** (Phase 02).
5. **Answer the AI interviewer's questions** for each skill (Phase 03). You can:
   - **Skip** a skill with the "Skip Skill →" button.
   - **Finish all** remaining skills with the "Finish All →" button.
6. **View your Intelligence Dashboard** (Phase 04) with:
   - Readiness score and skill gap analysis
   - Weekly learning plans with curated resources
   - YouTube videos at 3 difficulty levels
7. **Download your PDF report** using the "◈ DOWNLOAD PDF REPORT" button.

---

## ☁️ Deployment (Streamlit Cloud)

1. Push your code to GitHub (already done).
2. Go to [share.streamlit.io](https://share.streamlit.io).
3. Click **"New App"** and select your repository.
4. Set the main file to `main.py`.
5. In **"Advanced settings" → Secrets**, paste the contents of your `.env` file.
6. Click **"Deploy"**.

Your app will be live at `https://your-app-name.streamlit.app`.

---

## 🔒 Security

- **`.env` is gitignored**: Your API keys are never committed to version control.
- **`.env.example` contains only placeholders**: Safe for public repositories.
- **GitHub Push Protection**: The repository has been verified to contain no secrets.
- **Streamlit Secrets**: On deployment, keys are stored securely in Streamlit's encrypted secrets manager.

---

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/amazing-feature`.
3. Commit your changes: `git commit -m "Add amazing feature"`.
4. Push to the branch: `git push origin feature/amazing-feature`.
5. Open a Pull Request.

---

## 📜 License

This project is open source and available for educational and personal use.

---

<p align="center">
  <b>Built with 🧠 by Yash Thakre</b><br>
  <i>For the Catalyst Hackathon 2026</i>
</p>
