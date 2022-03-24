from pydantic import BaseModel

from oplc.model import Experience, Job, Skill, JobRecommendation

from typing import Callable, TypeVar

T = TypeVar('T')
U = TypeVar('U')
View = Callable[[T], U]


class JobJson(BaseModel, frozen=True):
    name: str

    @staticmethod
    def view(m: Job) -> "JobJson":
        return JobJson(name=m.name)


class SkillJson(BaseModel, frozen=True):
    name: str

    @staticmethod
    def view(m: Skill) -> "SkillJson":
        return SkillJson(name=m.name)

    def decode(self) -> Skill:
        return Skill(name=self.name)


class ExperienceJson(BaseModel, frozen=True):
    name: str
    exp_type: str

    @staticmethod
    def view(m: Experience) -> "ExperienceJson":
        return ExperienceJson(name=m.name, exp_type=m.exp_type)

    def decode(self) -> Experience:
        return Experience(name=self.name, exp_type=self.exp_type)


def view_jobs_json(jobs: list[Job]) -> list[JobJson]:
    return [JobJson.view(m) for m in jobs]


def view_skills_json(skills: list[Skill]) -> list[SkillJson]:
    return [SkillJson.view(c) for c in skills]


def view_experiences_json(experiences: list[Experience]) -> list[ExperienceJson]:
    return [ExperienceJson.view(c) for c in experiences]


def decode_experiences_json(experiences: list[ExperienceJson]) -> list[Experience]:
    return [x.decode() for x in experiences]


class JobWithScoreJson(BaseModel):
    job: JobJson
    score: float


class JobRecommendationJson(BaseModel):
    scores: list[JobWithScoreJson]

    @staticmethod
    def view(job_recommendation: JobRecommendation) -> "JobRecommendationJson":
        scores = [
            JobWithScoreJson(job=JobJson.view(m), score=s)
            for m, s in job_recommendation.items()]
        return JobRecommendationJson(scores=scores)
