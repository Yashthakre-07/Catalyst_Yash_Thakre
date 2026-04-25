from pydantic import BaseModel
from typing import Literal

class SkillAssessment(BaseModel):
    skill_name: str
    required_level: int
    claimed_level: int
    assessed_level: int
    gap_score: int
    priority_score: float = 0.0
    category: Literal["STRONG", "DEVELOPING", "GAP"]
    assessment_reasoning: str
