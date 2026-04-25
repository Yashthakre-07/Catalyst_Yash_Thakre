import json
import os
from loguru import logger

from models.candidate import CandidateProfile
from models.skill import SkillAssessment
from models.learning_plan import LearningPlan

from parsers.resume_parser import parse_resume
from parsers.jd_parser import parse_jd

from agent.assessor import get_next_question
from agent.scorer import score_skill
from agent.planner import generate_learning_plan

class AssessmentAgent:
    """
    Manages state and coordinates the full pipeline of the AI Skill Assessment Agent.
    """
    
    def __init__(self):
        self.candidate_profile = None
        self.required_skills = []
        self.current_skill_index = 0
        self.conversation_history = {} # skill_name -> list of dicts
        self.skill_assessments = []
        self.learning_plan = None
        
    def parse_documents(self, resume_text: str, jd_text: str):
        """Phase 1: Parse JD and Resume."""
        logger.info("Parsing resume...")
        self.candidate_profile = parse_resume(resume_text)
        
        logger.info("Parsing job description...")
        self.required_skills = parse_jd(jd_text)
        
        # Initialize conversation history for each required skill
        for skill in self.required_skills:
            self.conversation_history[skill["skill_name"]] = []
            
        self.current_skill_index = 0
        self.skill_assessments = []
        self.learning_plan = None
        
    def get_current_skill(self) -> dict:
        """Returns the current skill being assessed."""
        if self.current_skill_index < len(self.required_skills):
            return self.required_skills[self.current_skill_index]
        return None
        
    def get_next_question(self) -> dict:
        """Phase 2: Get next question for the current skill."""
        current_skill = self.get_current_skill()
        if not current_skill:
            return {"type": "complete", "reason": "No more skills to assess."}
            
        skill_name = current_skill["skill_name"]
        history = self.conversation_history[skill_name]
        
        decision = get_next_question(
            skill_name=skill_name,
            candidate_profile=self.candidate_profile,
            conversation_so_far=history
        )
        
        if decision.get("type") == "question":
            # Add agent's question to history
            self.conversation_history[skill_name].append({
                "role": "assistant",
                "content": decision["content"]
            })
            
        return decision

    def process_answer(self, answer: str):
        """Phase 2: Store candidate's answer for the current skill."""
        current_skill = self.get_current_skill()
        if not current_skill:
            return
            
        skill_name = current_skill["skill_name"]
        self.conversation_history[skill_name].append({
            "role": "user",
            "content": answer
        })
        
    def score_current_skill(self) -> SkillAssessment:
        """Phase 3: Score the current skill and move to the next."""
        current_skill = self.get_current_skill()
        if not current_skill:
            return None
            
        skill_name = current_skill["skill_name"]
        required_level = current_skill["required_level"]
        is_required = current_skill.get("is_required", True)
        history = self.conversation_history[skill_name]
        
        # Estimate claimed level
        claimed_skills = [s.lower() for s in self.candidate_profile.skills_from_resume]
        claimed_level = 5 if skill_name.lower() in claimed_skills else 1
        
        assessment = score_skill(
            skill_name=skill_name,
            required_level=required_level,
            claimed_level=claimed_level,
            is_required=is_required,
            conversation=history
        )
        
        self.skill_assessments.append(assessment)
        self.current_skill_index += 1
        return assessment
        
    def generate_plan(self) -> LearningPlan:
        """Phase 4: Generate the personalized learning plan."""
        logger.info("Generating learning plan from assessments...")
        # Simplistic target role derivation (first sentence of JD or generic)
        target_role = "Target Role based on JD"
        
        self.learning_plan = generate_learning_plan(
            candidate_profile=self.candidate_profile,
            target_role=target_role,
            skill_assessments=self.skill_assessments
        )
        return self.learning_plan


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    logger.info("Initializing Agent Core test...")
    agent = AssessmentAgent()
    
    # Load sample data
    with open("data/sample_jd.txt", "r") as f:
        jd_text = f.read()
    with open("data/sample_resume.txt", "r") as f:
        resume_text = f.read()
        
    agent.parse_documents(resume_text, jd_text)
    
    print(f"\nCandidate: {agent.candidate_profile.name}")
    print(f"Skills to assess: {[s['skill_name'] for s in agent.required_skills]}\n")
    
    # Assess first 2 skills for testing
    skills_to_test = 2
    for _ in range(min(skills_to_test, len(agent.required_skills))):
        current = agent.get_current_skill()
        print(f"--- Assessing {current['skill_name']} ---")
        
        while True:
            decision = agent.get_next_question()
            if decision["type"] == "complete":
                print(f"[Agent]: {decision.get('reason')}")
                break
                
            print(f"[Agent]: {decision['content']}")
            
            # Mock candidate answer
            answer = "I have basic knowledge but nothing advanced."
            print(f"[Candidate]: {answer}\n")
            agent.process_answer(answer)
            
        assessment = agent.score_current_skill()
        print(f"--> Score: {assessment.assessed_level}/10. Category: {assessment.category}\n")
        
    print("\n--- Generating Learning Plan ---")
    plan = agent.generate_plan()
    print(f"Total Weeks: {plan.total_duration_weeks}")
    print(f"Summary: {plan.summary}")
