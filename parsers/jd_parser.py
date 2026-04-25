import json
from utils.ai_client import AIClient
from agent.prompts import SKILL_EXTRACTOR_PROMPT
from loguru import logger

def parse_jd(jd_text: str) -> list[dict]:
    """
    Parses a job description to extract required skills.
    
    Args:
        jd_text (str): The raw text of the job description.
        
    Returns:
        list[dict]: A list of skill dictionaries extracted.
    """
    client = AIClient()
    prompt = SKILL_EXTRACTOR_PROMPT.replace("__JD_TEXT__", jd_text)
    
    logger.info("Extracting skills from job description...")
    response_text = client.complete_with_retry(
        system_prompt="You are an expert AI extraction system.",
        user_message=prompt
    )
    
    try:
        skills = json.loads(response_text)
        if not skills or not isinstance(skills, list):
            raise ValueError("Empty or invalid skill list")
        return skills
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"AI skill extraction failed or returned empty: {e}. Using fallback heuristics.")
        # Fallback: Simple keyword extraction if AI fails
        fallbacks = []
        common_skills = ["Python", "JavaScript", "SQL", "React", "Docker", "AWS", "FastAPI", "communication", "leadership"]
        jd_lower = jd_text.lower()
        for s in common_skills:
            if s.lower() in jd_lower:
                fallbacks.append({"skill_name": s, "required_level": 7, "is_required": True, "context": "Extracted via keyword match."})
        
        if not fallbacks:
            # Absolute last resort
            fallbacks = [{"skill_name": "General Technical Competency", "required_level": 5, "is_required": True, "context": "Default skill due to extraction issues."}]
        
        return fallbacks
