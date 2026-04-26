import json
from models.candidate import CandidateProfile
from utils.ai_client import AIClient
from agent.prompts import RESUME_PARSER_PROMPT
from loguru import logger

def parse_resume(resume_text: str) -> CandidateProfile:
    """
    Parses a resume to extract the candidate profile.
    """
    client = AIClient()
    prompt = RESUME_PARSER_PROMPT.replace("__RESUME_TEXT__", resume_text)
    
    logger.info("Extracting candidate profile from resume...")
    response_text = client.complete_with_retry(
        system_prompt="You are an expert AI talent acquisition system.",
        user_message=prompt
    )
    
    try:
        data = json.loads(response_text)
        data['resume_text'] = resume_text
        return CandidateProfile(**data)
    except Exception as e:
        logger.error(f"Failed to parse resume: {e}")
        logger.debug(f"Raw response: {response_text}")
        return CandidateProfile(
            name="Unknown Candidate",
            current_role="Unknown",
            years_experience=0,
            summary="Profile extracted with limited intelligence due to parsing error.",
            skills_from_resume=[],
            resume_text=resume_text
        )
