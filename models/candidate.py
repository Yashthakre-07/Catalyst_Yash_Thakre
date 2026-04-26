from pydantic import BaseModel

class CandidateProfile(BaseModel):
    name: str
    current_role: str
    years_experience: int
    summary: str = ""
    skills_from_resume: list[dict] # Each dict: {"name": str, "estimated_level": int}
    resume_text: str
