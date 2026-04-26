import json
from loguru import logger
from utils.ai_client import AIClient
from agent.prompts import SCORER_PROMPT
from models.skill import SkillAssessment
from agent.assessor import format_conversation

def score_skill(
    skill_name: str,
    required_level: int,
    claimed_level: int,
    is_required: bool,
    conversation: list[dict]
) -> SkillAssessment:
    """
    Scores a candidate's proficiency in a skill based on their conversation.
    Calculates priority_score based on gap and criticality.
    """
    client = AIClient()
    transcript = format_conversation(conversation)
    
    prompt = SCORER_PROMPT.replace("__SKILL_NAME__", skill_name)
    prompt = prompt.replace("__REQUIRED_LEVEL__", str(required_level))
    prompt = prompt.replace("__CLAIMED_LEVEL__", str(claimed_level))
    prompt = prompt.replace("__FULL_QA_TRANSCRIPT__", transcript)
    
    logger.info(f"Scoring candidate on {skill_name}...")
    response_text = client.complete_with_retry(
        system_prompt="You are an expert technical assessor.",
        user_message=prompt,
        skill_context=skill_name
    )
    
    try:
        data = json.loads(response_text)
        
        # Ensure gap_score matches our formula
        assessed_level = data.get("assessed_level", 0)
        actual_gap = required_level - assessed_level
        data["gap_score"] = actual_gap
        
        # Calculate Priority Score: (gap * 0.6) + (criticality * 0.4)
        # Criticality: 10 if required, 5 if nice-to-have
        criticality = 10 if is_required else 5
        priority_score = (actual_gap * 0.6) + (criticality * 0.4)
        data["priority_score"] = round(priority_score, 2)

        # Ensure category aligns with our strict definitions
        if assessed_level >= 8:
            data["category"] = "STRONG"
        elif assessed_level >= 5:
            data["category"] = "DEVELOPING"
        else:
            data["category"] = "GAP"
            
        assessment = SkillAssessment(**data)
        return assessment
    except Exception as e:
        logger.error(f"Failed to parse skill assessment for {skill_name}: {e}")
        logger.debug(f"Raw response: {response_text}")
        
        # Safe fallback
        return SkillAssessment(
            skill_name=skill_name,
            required_level=required_level,
            claimed_level=claimed_level,
            assessed_level=1,
            gap_score=required_level - 1,
            category="GAP",
            assessment_reasoning="Failed to score assessment properly due to unexpected LLM response.",
            candidate_feedback="We were unable to generate specific feedback for this skill at this time."
        )
