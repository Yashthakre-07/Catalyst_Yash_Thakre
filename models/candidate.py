from pydantic import BaseModel

class CandidateProfile(BaseModel):
    name: str
    current_role: str
    years_experience: int
    skills_from_resume: list[str]
    resume_text: str
