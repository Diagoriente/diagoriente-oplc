"""Views, transform core data types for presentation
"""

from pydantic import BaseModel

from oplc import core
from oplc.model import Model
import numpy as np
import networkx as nx

from typing import Tuple, Optional, Callable


JobIdJson = str

def job_id_json(job_id: core.JobId) -> JobIdJson:
    return str(job_id)


SkillIdJson = str

def skill_id_json(skill_id: core.SkillId) -> SkillIdJson:
    return str(skill_id)


ExperienceIdJson = str

def experience_id_json(experience_id: core.ExperienceId) -> ExperienceIdJson:
    return str(experience_id)


def experience_id_from_json(experience_id: ExperienceIdJson) -> core.ExperienceId:
    return int(experience_id)



class ExperienceJson(BaseModel):
    name: str
    exp_type: str


def experiences_json(model: Model) -> dict[ExperienceIdJson, ExperienceJson]:
    return {experience_id_json(i): ExperienceJson(name=e.name, exp_type=e.exp_type)
            for i, e in model.experiences.items()
            }


class SkillJson(BaseModel, frozen=True):
    name: str


def skill_json(skill: core.Skill) -> SkillJson:
    return SkillJson(name=skill.name)

def skills_json(model: Model) -> dict[SkillIdJson, SkillJson]:
    return {skill_id_json(i): SkillJson(name=s.name)
            for i, s in model.skills.items()
            }


class JobJson(BaseModel):
    id: JobIdJson
    name: str


def job_json(job: core.Job) -> JobJson:
    return JobJson(id=job_id_json(job.id), name=job.name)

def jobs_json(model: Model) -> dict[JobIdJson, JobJson]:
    return {job_id_json(i):job_json(j)
            for i, j in model.jobs.items()
            }


class SkillGraphJson(BaseModel):
    edges: list[Tuple[SkillIdJson, SkillIdJson]]
    layout: dict[SkillIdJson, Tuple[np.float64, np.float64]]
    centrality: dict[SkillIdJson, np.float64]


def skill_graph_json(
        graph: core.SkillGraph,
        ) -> SkillGraphJson:
    edges: list[Tuple[SkillIdJson, SkillIdJson]] = [
            (skill_id_json(
                u # type:ignore
                ),
            skill_id_json(
                v # type:ignore
                )
            )
            for u, v in graph.graph.edges
            ]
    layout = {skill_id_json(s): (x, y) for s, [x, y] in graph.layout.items()}
    centrality = {skill_id_json(s): c for s, c in  graph.centrality.items()}
    return SkillGraphJson(edges=edges, layout=layout, centrality=centrality)


class JobWithScoreJson(BaseModel):
    job: JobJson
    score: float

class JobRecommendationJson(BaseModel):
    scores: list[JobWithScoreJson]
    skill_graph: Optional[SkillGraphJson]


def job_recommendation_json(
        model: Model,
        experiences: list[ExperienceIdJson],
        return_graph: bool,
        skill_centrality_measure: Callable[[nx.Graph], float]
        ) -> JobRecommendationJson:
    jr = core.job_recommendation(
                model.experiences_skills,
                model.jobs_skills,
                [experience_id_from_json(e) for e in experiences],
                return_graph=return_graph,
                skill_centrality_measure=skill_centrality_measure,
                )
    scores = [
        JobWithScoreJson(job=job_json(model.jobs[j]), score=s)
        for j, s in jr.items()
        ]

    if jr.skill_graph is not None:
        graph = skill_graph_json(jr.skill_graph)
    else:
        graph = None

    return JobRecommendationJson(scores=scores, skill_graph=graph)


