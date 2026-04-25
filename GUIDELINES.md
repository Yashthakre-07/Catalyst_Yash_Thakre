# Agent Guidelines

## 1. Agent Overview
This is an AI-Powered Skill Assessment & Personalised Learning Plan Agent. It parses a candidate's resume and a job description, conducts a conversational technical screen on the required skills to determine true proficiency, and outputs a personalized, week-by-week learning plan to address any skill gaps.

## 2. Architecture Decisions Table

| Decision | Alternative | Why We Chose This |
| --- | --- | --- |
| Provider-agnostic AI wrapper | LangChain / LlamaIndex | Allows us to seamlessly switch between Gemini and Groq with native SDKs. Zero bloat, fast execution, full control over parsing. |
| Raw SDK | AutoGen | Keeps the agent loop simple, debuggable, and explicit for a deterministic chat application without unneeded complexity. |
| Pydantic v2 | Plain Dicts | Ensures strict data validation across the pipeline, critical when depending on LLM-generated JSON outputs. |
| Streamlit | React / Next.js | Perfect for rapid, data-heavy Python applications. Allows us to focus 100% on the core agent while maintaining a clean UI. |
| JSON state | SQL Database | Simpler to implement for a hackathon and easily portable. |
| PyMuPDF (fitz) | PyPDF2 | Significantly better and faster text extraction, handles modern PDFs natively. |
| Manual retry logic | Retrying libraries | Gives exact control over modifying the prompt upon JSON decode failures, appending specific instructions to help the model recover. |

## 3. Data Flow

```text
JD + Resume
   │
   ▼
[Parser] ───► CandidateProfile + RequiredSkills
   │
   ▼
[Assessor Loop] ───► ConversationHistory per skill
   │
   ▼
[Scorer] ───► SkillAssessment[]
   │
   ▼
[Planner] ───► LearningPlan
   │
   ▼
[UI] ───► User
```

## 4. Why raw SDK over LangChain
LangChain is powerful but introduces opaque abstractions that are difficult to debug when prompts or parsers fail. Building the agent loop manually allows us to explicitly manage JSON parsing, retries, system prompts, and state management, providing clear code that junior engineers can easily read and learn from.

## 5. Why provider-agnostic wrapper
- **Gemini 1.5 Flash:** Offers strong reasoning capabilities, large context windows, and a generous free tier. It is slightly slower but highly dependable for complex system instructions.
- **Groq (LLaMA 3.3 70B):** Offers extremely fast inference speeds which are ideal for a chat-like conversational assessment.

The `AIClient` wrapper handles the differences in API structure natively so the rest of the application remains clean.

## 6. Scoring algorithm explanation
- The user is assessed and given a score from 1-10.
- `gap_score = required_level - assessed_level`
- Categories are straightforward: `STRONG` (>=8), `DEVELOPING` (5-7), `GAP` (<=4).
- A priority formula identifies the most critical gaps: `priority_score = (gap_score * 0.6) + (business_criticality * 0.4)` where criticality is 10 if "required", 5 if "nice-to-have".

## 7. How to add new skills to resource database
To add new skills, simply update the `data/skill_resources.json` file. Create a new key with the skill name and provide a list of JSON objects matching the `Resource` Pydantic model (`title`, `url`, `type`, `estimated_hours`, `why_recommended`).

## 8. How to add a third AI provider (e.g. OpenAI) to AIClient
In `utils/ai_client.py`:
1. Add an `elif self.provider == "openai":` block in `__init__` and configure the client.
2. In `complete()`, add the corresponding API call structure, extracting and returning just the raw text output.
3. Update `config/settings.py` and `.env.example` to include the `OPENAI_API_KEY`.

## 9. Environment variables reference
- `AI_PROVIDER`: "gemini" or "groq"
- `GEMINI_API_KEY`: API key for Google Gemini.
- `GEMINI_MODEL`: Model name, defaults to "gemini-1.5-flash".
- `GROQ_API_KEY`: API key for Groq.
- `GROQ_MODEL`: Model name, defaults to "llama-3.3-70b-versatile".
- `LOG_LEVEL`: For python-loguru logger.
- `MAX_QUESTIONS_PER_SKILL`: The cap on conversation turns per skill (3).
