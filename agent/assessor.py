import json
from loguru import logger
from utils.ai_client import AIClient
from agent.prompts import ASSESSOR_PROMPT
from models.candidate import CandidateProfile
from config import settings

def format_conversation(conversation: list[dict]) -> str:
    """
    Formats the conversation history into a readable string for the LLM.
    
    Args:
        conversation: List of dictionaries with 'role' ('assistant' or 'user') and 'content'.
    
    Returns:
        A formatted string transcript.
    """
    if not conversation:
        return "No conversation yet."
    
    transcript = []
    for msg in conversation:
        role = "Agent" if msg["role"] == "assistant" else "Candidate"
        transcript.append(f"{role}: {msg['content']}")
    
    return "\n\n".join(transcript)

def get_next_question(
    skill_name: str,
    candidate_profile: CandidateProfile,
    conversation_so_far: list[dict]
) -> dict:
    """
    Determines the next assessment question or completes the assessment.
    
    Args:
        skill_name: The skill being assessed.
        candidate_profile: The extracted candidate profile.
        conversation_so_far: The conversation history for this skill.
        
    Returns:
        A dictionary with "type" ("question" or "complete") and "content" or "reason".
    """
    # Number of questions asked by the agent so far
    question_number = sum(1 for msg in conversation_so_far if msg.get("role") == "assistant") + 1
    
    if question_number > settings.MAX_QUESTIONS_PER_SKILL:
        return {
            "type": "complete",
            "reason": f"Reached the maximum of {settings.MAX_QUESTIONS_PER_SKILL} questions for this skill."
        }

    client = AIClient()
    
    background = (
        f"Name: {candidate_profile.name}\n"
        f"Current Role: {candidate_profile.current_role}\n"
        f"Years Experience: {candidate_profile.years_experience}\n"
        f"Skills on Resume: {', '.join(candidate_profile.skills_from_resume)}"
    )
    
    transcript = format_conversation(conversation_so_far)
    
    prompt = ASSESSOR_PROMPT.replace("__SKILL_NAME__", skill_name)
    prompt = prompt.replace("__CANDIDATE_BACKGROUND__", background)
    prompt = prompt.replace("__CONVERSATION_SO_FAR__", transcript)
    prompt = prompt.replace("__QUESTION_NUMBER__", str(question_number))
    
    logger.info(f"Generating question {question_number} for {skill_name}...")
    response_text = client.complete_with_retry(
        system_prompt="You are an expert technical interviewer.",
        user_message=prompt,
        skill_context=skill_name
    )
    
    try:
        decision = json.loads(response_text)
        
        # FORCE 3 QUESTIONS: If it's less than 3, and it tries to complete, override it
        if decision.get("type") == "complete" and question_number <= 3:
            logger.warning(f"Agent tried to complete {skill_name} at Q{question_number}. Forcing question.")
            # Re-run with a stricter prompt or just return a generic fallback
            return {
                "type": "question",
                "content": f"Before we move on, could you share more about your experience with {skill_name}, specifically in a production or complex environment?"
            }
            
        return decision
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse assessor decision: {e}")
        # Fallback to a question instead of complete to prevent skipping the demo
        return {
            "type": "question",
            "content": f"I'm interested in your practical experience with {skill_name}. Could you walk me through a complex scenario where you applied this skill to solve a real-world problem?"
        }
