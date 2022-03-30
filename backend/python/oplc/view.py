"""Views, transform core data types for presentation
"""

from pydantic import BaseModel

from oplc import core
from oplc.model import Model
import numpy as np
from oplc.core import ExperienceId, SkillId, JobId

from typing import Tuple, Optional


class ExperienceJson(BaseModel):
    name: str
    exp_type: str


def experiences_json(model: Model) -> dict[ExperienceId, ExperienceJson]:
    return {i: ExperienceJson(name=e.name, exp_type=e.exp_type)
            for i, e in model.experiences.items()
            }


class SkillJson(BaseModel, frozen=True):
    name: str


def skill_json(skill: core.Skill) -> SkillJson:
    return SkillJson(name=skill.name)

def skills_json(model: Model) -> dict[SkillId, SkillJson]:
    return {i: SkillJson(name=s.name)
            for i, s in model.jobs.items()
            }


class JobJson(BaseModel):
    name: str


def jobs_json(model: Model) -> dict[JobId, JobJson]:
    return {i:JobJson(name=j.name)
            for i, j in model.jobs.items()
            }

class SkillGraphJson(BaseModel):
    edges: list[Tuple[SkillId, SkillId]]
    layout: dict[SkillId, Tuple[np.float64, np.float64]]

def skill_graph_json(
        graph: core.SkillGraph,
        ) -> SkillGraphJson:
    edges: list[Tuple[SkillId, SkillId]] = [(u, v) for u, v in graph.graph.edges]
    layout = {s: (x, y) for s, [x, y] in graph.layout.items()}
    return SkillGraphJson(edges=edges, layout=layout)

class JobWithScoreJson(BaseModel):
    job: JobId
    score: float

class JobRecommendationJson(BaseModel):
    scores: list[JobWithScoreJson]
    graph: Optional[SkillGraphJson]


def job_recommendation_json(
        model: Model,
        experiences: list[ExperienceId],
        return_graph: bool,
        ) -> JobRecommendationJson:
    jr = core.job_recommendation(
                model.experiences_skills,
                model.jobs_skills,
                experiences,
                return_graph=return_graph,
                )
    scores = [
        JobWithScoreJson(job=j, score=s)
        for j, s in jr.items()
        ]

    if jr.skill_graph is not None:
        graph = skill_graph_json(jr.skill_graph)
    else:
        graph = None

    return JobRecommendationJson(scores=scores, graph=graph)


