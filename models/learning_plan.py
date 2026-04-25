from pydantic import BaseModel, Field
from typing import Literal, Optional, List

class Resource(BaseModel):
    title: str
    url: str
    type: str
    description: str = ""

class YoutubeLevel(BaseModel):
    title: str
    url: str
    channel: str
    why: str

class YoutubeResources(BaseModel):
    easy: YoutubeLevel
    medium: YoutubeLevel
    hard: YoutubeLevel

class WeeklyTopic(BaseModel):
    week_label: str
    title: str
    objective: str
    what_to_study: List[str]
    documentation: List[Resource]
    youtube: YoutubeResources
    extra_resources: List[Resource]
    hands_on: str
    milestone: str

class SkillPlan(BaseModel):
    skill_name: str
    category: Literal["GAP", "DEVELOPING", "STRONG"]
    total_weeks: int
    color: str # red | amber | green
    current_level: int
    target_level: int
    adjacent_skills: List[str] = []
    topics: List[WeeklyTopic] = []
    
    # Metadata support
    assessment_reasoning: str = ""
    why_this_matters: str = ""

class AdjacentLeverage(BaseModel):
    existing_skill: str
    unlocks_skill: str
    message: str

class LearningPlan(BaseModel):
    candidate_name: str
    target_role: str
    total_weeks: int
    readiness_score: int
    summary: str
    skills: List[SkillPlan]
    assessment_date: str = "Today"
    adjacent_leverages: List[AdjacentLeverage] = []
