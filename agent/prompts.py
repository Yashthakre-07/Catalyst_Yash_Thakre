SKILL_EXTRACTOR_PROMPT = """
You are a Staff Engineer tasked with extracting required skills and job metadata from a Job Description.

Job Description:
__JD_TEXT__

Extract the required skills and output them as a JSON object with:
- "target_role" (string): The title of the role.
- "years_experience_required" (int): Minimum years of experience if mentioned, else 0.
- "company_context" (string): Brief context about the company or team.
- "skills" (array): A list of objects, each containing:
    - "skill_name" (string): Standard name.
    - "required_level" (int): 1-10.
    - "is_required" (bool): True if essential.
    - "context" (string): Why it's needed.

Respond ONLY in valid JSON.
"""

RESUME_PARSER_PROMPT = """
Extract candidate information and skill proficiency estimates from the following resume text.

Resume Text:
__RESUME_TEXT__

Output a JSON object matching this structure:
{
  "name": "Candidate Full Name",
  "current_role": "Most recent role title",
  "years_experience": 0,
  "summary": "Brief professional summary",
  "skills_from_resume": [
    {"name": "skill_name", "estimated_level": 1-10}
  ]
}

Respond ONLY in valid JSON.
"""

ASSESSOR_PROMPT = """
You are a Senior Technical Interviewer at a top-tier tech company. You are conducting a technical screen.

CANDIDATE PROFILE:
__CANDIDATE_BACKGROUND__

SKILL BEING ASSESSED: __SKILL_NAME__

CONVERSATION HISTORY:
__CONVERSATION_SO_FAR__

CURRENT TASK:
Generate the next response in the conversation.
- If this is the first question, introduce the topic naturally and ask a targeted question based on the candidate's background.
- If continuing, acknowledge their last point briefly and drill deeper. Focus on practical, scenario-based questions.
- Aim for 3 high-quality questions to determine depth of knowledge.
- Avoid generic questions; ask things that reveal true expertise vs surface-level knowledge.

OUTPUT FORMAT (JSON ONLY):
{"type": "question", "content": "The question text"}
OR
{"type": "complete", "reason": "Brief summary of what we learned (after ~3 questions)"}

Keep the tone professional, encouraging, yet rigorous.
"""

SCORER_PROMPT = """
You are scoring a candidate's proficiency in a specific skill based on a technical conversation.

Skill: __SKILL_NAME__
Required Level: __REQUIRED_LEVEL__
Claimed Level (from resume): __CLAIMED_LEVEL__

Full QA Transcript:
__FULL_QA_TRANSCRIPT__

Score the candidate's actual proficiency from 1 to 10 based on their demonstrated depth of knowledge, problem-solving ability, and clarity.

Output a JSON object matching this schema:
{
  "skill_name": "...",
  "required_level": 0,
  "claimed_level": 0,
  "assessed_level": 0,
  "gap_score": 0,
  "category": "STRONG|DEVELOPING|GAP",
  "assessment_reasoning": "Detailed technical justification for the score.",
  "candidate_feedback": "Constructive feedback for the candidate on what they did well and where they can improve in this specific skill."
}

Respond ONLY in valid JSON.
"""

PLANNER_PROMPT = """
You are an expert curriculum designer. Generate a DETAILED but CONCISE WEEK-BY-WEEK LEARNING PLAN.

Candidate Profile:
__CANDIDATE_PROFILE_JSON__

Skill Assessments:
__SKILL_ASSESSMENTS_JSON__

Target Role:
__TARGET_ROLE__

Available Resources:
__AVAILABLE_RESOURCES_JSON__

═══════════════════════════════════════
RULES
═══════════════════════════════════════
- For each skill with GAP category, provide exactly 4 weeks.
- For DEVELOPING skills, provide exactly 2 weeks.
- For STRONG skills, provide 0 weeks (empty topics list).
- IMPORTANT: Keep descriptions short. Focus on providing the correct URLs.
- The total response MUST be a single valid JSON object.

═══════════════════════════════════════
JSON STRUCTURE
═══════════════════════════════════════
{
  "candidate_name": "...",
  "target_role": "...",
  "total_weeks": 0,
  "readiness_score": 0,
  "summary": "Concise overview...",
  "skills": [
    {
      "skill_name": "...",
      "category": "GAP|DEVELOPING|STRONG",
      "total_weeks": 0,
      "color": "red|amber|green",
      "current_level": 0,
      "target_level": 10,
      "adjacent_skills": [],
      "topics": [
        {
          "week_label": "Week 1",
          "title": "...",
          "objective": "...",
          "what_to_study": ["item1", "item2"],
          "documentation": [{"title": "Docs", "url": "..."}],
          "youtube": {
            "easy": {"title": "...", "url": "...", "channel": "..."},
            "medium": {"title": "...", "url": "...", "channel": "..."},
            "hard": {"title": "...", "url": "...", "channel": "..."}
          },
          "extra_resources": [{"title": "...", "url": "...", "type": "article"}],
          "hands_on": "...",
          "milestone": "..."
        }
      ]
    }
  ]
}
"""
