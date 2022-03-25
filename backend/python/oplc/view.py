"""Views, transform core data types for presentation
"""

from pydantic import BaseModel

from oplc import core
from oplc.model import Model


class ExperienceJson(BaseModel):
    name: str
    exp_type: str


def experiences_json(model: Model) -> list[ExperienceJson]:
    return [
            ExperienceJson(name=e.name, exp_type=e.exp_type)
            for e in core.experiences(model.experiences_skills)
            ]


class SkillJson(BaseModel):
    name: str


def skills_json(model: Model) -> list[SkillJson]:
    return [
            SkillJson(name=s.name)
            for s in core.skills(model.jobs_skills)
            ]


class JobJson(BaseModel):
    name: str


def jobs_json(model: Model) -> list[JobJson]:
    return [
            JobJson(name=j.name)
            for j in core.jobs(model.jobs_skills)
            ]


class JobWithScoreJson(BaseModel):
    job: core.Job
    score: float


class JobRecommendationJson(BaseModel):
    scores: list[JobWithScoreJson]


def job_recommendation_json(
        model: Model,
        experiences: list[core.Experience],
        ) -> JobRecommendationJson:
    jr = core.job_recommendation(
                model.experiences_skills,
                model.jobs_skills,
                experiences,
                )
    scores = [
        JobWithScoreJson(job=m, score=s)
        for m, s in jr.items()
        ]
    return JobRecommendationJson(scores=scores)


