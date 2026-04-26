import json
from utils.ai_client import AIClient
from agent.prompts import SKILL_EXTRACTOR_PROMPT
from loguru import logger

def parse_jd(jd_text: str) -> dict:
    """
    Parses a job description to extract required skills and metadata.
    """
    client = AIClient()
    prompt = SKILL_EXTRACTOR_PROMPT.replace("__JD_TEXT__", jd_text)
    
    logger.info("Extracting skills and metadata from JD...")
    response_text = client.complete_with_retry(
        system_prompt="You are an expert AI extraction system.",
        user_message=prompt
    )
    
    try:
        data = json.loads(response_text)
        if not data.get("skills"):
            raise ValueError("No skills found in JD.")
        return data
    except Exception as e:
        logger.warning(f"AI skill extraction failed: {e}. Using fallback.")
        # Fallback
        return {
            "target_role": "Target Role",
            "years_experience_required": 0,
            "company_context": "Not specified",
            "skills": [
                {"skill_name": "General Technical Competency", "required_level": 7, "is_required": True, "context": "Fallback skill."}
            ]
        }
