SKILL_EXTRACTOR_PROMPT = """
You are a Staff Engineer tasked with extracting required skills from a Job Description.

Job Description:
__JD_TEXT__

Extract the required skills and output them as a JSON array. For each skill, provide:
- "skill_name" (string): The standard name of the skill.
- "required_level" (int): From 1 to 10, how proficient the candidate needs to be based on the JD.
- "is_required" (bool): True if required, False if nice-to-have.
- "context" (string): Why it's needed based on the JD.

Respond ONLY in valid JSON. No explanation outside the JSON.
"""

RESUME_PARSER_PROMPT = """
Extract candidate information from the following resume text.

Resume Text:
__RESUME_TEXT__

Output a JSON object matching this structure:
{
  "name": "Candidate Full Name",
  "current_role": "Most recent role title",
  "years_experience": 0,
  "skills_from_resume": ["skill1", "skill2"]
}

Respond ONLY in valid JSON. No explanation outside the JSON.
"""

ASSESSOR_PROMPT = """
You are a Staff Engineer at a tech company doing a casual technical screen. 
We are assessing the candidate on the following skill:
Skill: __SKILL_NAME__

Candidate Background:
__CANDIDATE_BACKGROUND__

Conversation so far:
__CONVERSATION_SO_FAR__

Question Number: __QUESTION_NUMBER__

Generate the next response. Aim to ask exactly 3 questions per skill.
It should be a JSON object with EITHER:
{"type": "question", "content": "the question text"}
OR
{"type": "complete", "reason": "why we have enough data (usually after 3 questions)"}

Respond ONLY in valid JSON.
"""

SCORER_PROMPT = """
You are scoring a candidate's proficiency in a specific skill based on a technical conversation.

Skill: __SKILL_NAME__
Required Level: __REQUIRED_LEVEL__
Claimed Level (from resume): __CLAIMED_LEVEL__

Full QA Transcript:
__FULL_QA_TRANSCRIPT__

Score the candidate's actual proficiency from 1 to 10.
Calculate the gap_score (required_level - assessed_level).
Assign a category: STRONG (>=8), DEVELOPING (5-7), GAP (<=4).

Output a JSON object matching this schema:
{
  "skill_name": "...",
  "required_level": 0,
  "claimed_level": 0,
  "assessed_level": 0,
  "gap_score": 0,
  "category": "STRONG|DEVELOPING|GAP",
  "assessment_reasoning": "..."
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
