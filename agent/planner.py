import json
from loguru import logger
from utils.ai_client import AIClient
from agent.prompts import PLANNER_PROMPT
from models.candidate import CandidateProfile
from models.skill import SkillAssessment
from models.learning_plan import LearningPlan, SkillPlan
from utils.resource_finder import find_resources_for_skills

def generate_learning_plan(
    candidate_profile: CandidateProfile,
    target_role: str,
    skill_assessments: list[SkillAssessment]
) -> LearningPlan:
    """
    Generates a high-fidelity personalized learning plan based on candidate profile and skill gaps.
    """
    client = AIClient()
    
    # Identify skills to fetch resources for
    skills_to_develop = [sa.skill_name for sa in skill_assessments if sa.category in ("DEVELOPING", "GAP")]
    resources = find_resources_for_skills(skills_to_develop)
    
    # Dump inputs to JSON for prompt
    candidate_profile_json = candidate_profile.model_dump_json()
    skill_assessments_json = json.dumps([sa.model_dump() for sa in skill_assessments])
    available_resources_json = json.dumps(resources)
    
    # Use .replace() with the new double-underscore placeholders
    prompt = PLANNER_PROMPT.replace("__CANDIDATE_PROFILE_JSON__", candidate_profile_json)
    prompt = prompt.replace("__SKILL_ASSESSMENTS_JSON__", skill_assessments_json)
    prompt = prompt.replace("__TARGET_ROLE__", target_role)
    prompt = prompt.replace("__AVAILABLE_RESOURCES_JSON__", available_resources_json)
    
    schema_str = json.dumps(LearningPlan.model_json_schema(), indent=2)
    system_prompt = f"You are an expert curriculum designer and Staff Engineer. Respond ONLY in valid JSON matching the specified structure.\n\nSchema Reference:\n{schema_str}"
    
    logger.info("Generating high-fidelity learning plan...")
    
    response_text = client.complete_with_retry(
        system_prompt=system_prompt,
        user_message=prompt,
        max_tokens=4000
    )
    
    try:
        data = json.loads(response_text)
        learning_plan = LearningPlan(**data)
        return learning_plan
    except Exception as e:
        logger.error(f"Failed to parse learning plan: {e}")
        logger.debug(f"Raw response: {response_text}")
        
        # Build robust fallback
        total_assessed = sum(sa.assessed_level for sa in skill_assessments)
        total_required = sum(sa.required_level for sa in skill_assessments)
        readiness = int((total_assessed / max(total_required, 1)) * 100)
        
        fallback_skills = []
        for sa in skill_assessments:
            fallback_skills.append(SkillPlan(
                skill_name=sa.skill_name,
                category=sa.category,
                total_weeks=2 if sa.category != "STRONG" else 0,
                color="red" if sa.category == "GAP" else "amber" if sa.category == "DEVELOPING" else "green",
                current_level=sa.assessed_level,
                target_level=sa.required_level,
                adjacent_skills=[],
                topics=[]
            ))

        return LearningPlan(
            candidate_name=candidate_profile.name,
            target_role=target_role,
            total_weeks=max(4, sum(s.total_weeks for s in fallback_skills)),
            readiness_score=readiness,
            summary="Neural link established. Processing assessment results for strategic curriculum design. (Note: Using fallback intelligence due to synthesis interruption.)",
            skills=fallback_skills,
            adjacent_leverages=[]
        )
