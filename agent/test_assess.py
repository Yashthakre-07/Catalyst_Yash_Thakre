import os
import sys
import json
from loguru import logger

# Add project root to sys.path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.candidate import CandidateProfile
from agent.assessor import get_next_question
from agent.scorer import score_skill

def main():
    logger.info("Testing Agent Brain (Phase 2)...")
    
    # Setup mock candidate
    candidate = CandidateProfile(
        name="Alex Chen",
        current_role="Backend Engineer",
        years_experience=2,
        skills_from_resume=["Python", "Django", "SQL", "Git", "Linux"],
        resume_text="Mock resume text."
    )
    
    skill_name = "Docker"
    required_level = 7
    claimed_level = 0 # Not mentioned on resume
    
    print(f"\n--- Starting Assessment for: {skill_name} ---")
    print(f"Target Level: {required_level}")
    
    conversation_so_far = []
    
    # Mocking user input for a fully autonomous test script
    mock_candidate_answers = [
        "I haven't used Docker much, but I've heard it uses containers.",
        "A container is like a lightweight VM, I think? It packages code and dependencies.",
        "No, I don't know the difference between CMD and ENTRYPOINT."
    ]
    
    answer_idx = 0
    
    while True:
        # Agent generates a question
        decision = get_next_question(skill_name, candidate, conversation_so_far)
        
        if decision.get("type") == "complete":
            print("\n[Agent] Assessment Complete.")
            print(f"Reason: {decision.get('reason')}")
            break
            
        question = decision.get("content", "Error: No question provided.")
        print(f"\n[Agent]: {question}")
        conversation_so_far.append({"role": "assistant", "content": question})
        
        # Mock candidate response
        if answer_idx < len(mock_candidate_answers):
            answer = mock_candidate_answers[answer_idx]
            answer_idx += 1
        else:
            answer = "I don't know."
            
        print(f"[Candidate]: {answer}")
        conversation_so_far.append({"role": "user", "content": answer})

    print("\n--- Scoring Assessment ---")
    assessment = score_skill(
        skill_name=skill_name,
        required_level=required_level,
        claimed_level=claimed_level,
        conversation=conversation_so_far
    )
    
    print("\n[Final Skill Assessment JSON]")
    print(assessment.model_dump_json(indent=2))

if __name__ == "__main__":
    main()
