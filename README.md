# NeuralHire: AI Skill Assessment & Personalized Learning Agent

NeuralHire is a production-grade AI-powered system designed to assess candidate skills through autonomous technical screening and generate high-fidelity, personalized learning plans.

## 🚀 Features
- **Neural Sync Core**: Autonomous technical screening via Gemini and Groq.
- **Mastery Dashboard**: Cinematic, high-impact UI for visualizing skill gaps.
- **Intelligent Roadmap**: Personalized weekly learning plans with curated resource grids.
- **Neural PDF Export**: High-fidelity PDF reports with dashboard-like aesthetics.
- **Failover Logic**: Robust multi-key rotation and automatic failover system.

## 🛠️ Tech Stack
- **Frontend**: Streamlit (Neural Dark Theme)
- **AI Engine**: Google Gemini 1.5 Flash & Groq (Llama 3.3)
- **Backend**: Python (Pydantic, ReportLab)
- **Styling**: Custom Vanilla CSS with Glassmorphism

## 📦 Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Yashthakre-07/Catalyst_Yash_Thakre.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your `.env` file (see `.env.example`).
4. Run the application:
   ```bash
   streamlit run main.py
   ```

## 🔒 Security
The system uses a `.gitignore` to ensure sensitive API keys in the `.env` file are never uploaded to version control.
