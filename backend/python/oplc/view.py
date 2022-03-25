from pydantic import BaseModel

from oplc.core import Experience, Job, Skill, job_recommendation
from oplc.model import Model

from typing import Callable, TypeVar

T = TypeVar('T')
U = TypeVar('U')
View = Callable[[T], U]


class JobJson(BaseModel, frozen=True):
    name: str

def view_job_json(m: Job) -> JobJson:
    return JobJson(name=m.name)


def view_jobs_json(model: Model) -> list[JobJson]:
    jobs = model.jobs_skills.jobs()
    return [view_job_json(m) for m in jobs]


class SkillJson(BaseModel, frozen=True):
    name: str

def view_skill_json(m: Skill) -> SkillJson:
    return SkillJson(name=m.name)

def decode_skill_json(j: SkillJson) -> Skill:
    return Skill(name=j.name)


class ExperienceJson(BaseModel, frozen=True):
    name: str
    exp_type: str

def view_experience_json(m: Experience) -> ExperienceJson:
    return ExperienceJson(name=m.name, exp_type=m.exp_type)

def decode_experience_json(j: ExperienceJson) -> Experience:
    return Experience(name=j.name, exp_type=j.exp_type)


def view_skills_json(model: Model) -> list[SkillJson]:
    skills = model.experiences_skills.skills()
    return [view_skill_json(c) for c in skills]


def view_experiences_json(model: Model) -> list[ExperienceJson]:
    experiences = model.experiences_skills.experiences()
    return [view_experience_json(c) for c in experiences]

def decode_experiences_json(experiences: list[ExperienceJson]) -> list[Experience]:
    return [decode_experience_json(x) for x in experiences]



class JobWithScoreJson(BaseModel):
    job: JobJson
    score: float


class JobRecommendationJson(BaseModel):
    scores: list[JobWithScoreJson]

def view_job_recommendation_json(
        model: Model,
        experiences: list[Experience],
        ) -> JobRecommendationJson:
    jr = job_recommendation(
            model.experiences_skills,
            model.jobs_skills,
            experiences,
            )
    scores = [
        JobWithScoreJson(job=view_job_json(m), score=s)
        for m, s in jr.items()
        ]
    return JobRecommendationJson(scores=scores)


