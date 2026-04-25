from dotenv import load_dotenv
import os
import json

# Load .env before any app imports
load_dotenv()

from models.candidate import CandidateProfile
from models.skill import SkillAssessment
from agent.planner import generate_learning_plan

def test_planner():
    print("Testing Planner...")
    
    # Mock data
    candidate = CandidateProfile(
        name="Alex Chen",
        current_role="Backend Developer",
        years_experience=2,
        skills_from_resume=["Python", "Django", "SQL", "Git", "Linux"],
        resume_text="Alex is a developer with 2 years of experience."
    )
    
    target_role = "Backend Python Engineer"
    
    assessments = [
        SkillAssessment(
            skill_name="Python",
            required_level=9,
            claimed_level=7,
            assessed_level=8,
            gap_score=1,
            category="STRONG",
            assessment_reasoning="Alex knows Python well but lacks some advanced generator knowledge."
        ),
        SkillAssessment(
            skill_name="Docker",
            required_level=8,
            claimed_level=1,
            assessed_level=2,
            gap_score=6,
            category="GAP",
            assessment_reasoning="Alex has no practical experience with Docker, only read about it."
        ),
        SkillAssessment(
            skill_name="FastAPI",
            required_level=7,
            claimed_level=1,
            assessed_level=4,
            gap_score=3,
            category="GAP",
            assessment_reasoning="Alex knows Django, which helps, but needs to learn FastAPI specifics."
        ),
        SkillAssessment(
            skill_name="PostgreSQL",
            required_level=8,
            claimed_level=5,
            assessed_level=6,
            gap_score=2,
            category="DEVELOPING",
            assessment_reasoning="Alex knows basic SQL, but lacks advanced PostgreSQL features."
        )
    ]
    
    try:
        plan = generate_learning_plan(candidate, target_role, assessments)
        print("\n=== GENERATED LEARNING PLAN ===")
        print(plan.model_dump_json(indent=2))
        print("===============================\n")
    except Exception as e:
        print(f"Failed to generate plan: {e}")

if __name__ == "__main__":
    test_planner()
