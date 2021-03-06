from dataclasses import dataclass
from typing import Iterable, Tuple, Optional, Callable, NewType
import pandas as pa
from scipy.spatial.distance import pdist, squareform
import numpy as np
import numpy.typing as npt
import networkx as nx
from lenses import lens
from math import floor, sqrt
from datetime import datetime


# The objective of this application is to make job recommendations based on an
# individual job experiences and skills.
# Jobs, experiences and skills are identified by their names. An experience
# also has a type, personal or professional.


ExperienceId = int

@dataclass(frozen=True)
class Experience:
    id: ExperienceId
    name: str
    exp_type: str


SkillId = int


def mk_experiences(
        experiences: dict[int, tuple[str, str]]
        ) -> dict[int, Experience]:
    return {i: Experience(id=i, name=exp, exp_type=exp_type)
            for i, (exp, exp_type) in experiences.items()
        }


@dataclass(frozen=True)
class Skill:
    id: SkillId
    name: str


def mk_skills(skills: dict[int, str]) -> dict[int, Skill]:
    return {i: Skill(id=i, name=n) for i, n in skills.items()}

JobId = int

@dataclass
class Job:
    id: JobId
    name: str

def mk_jobs(jobs: dict[int, str]) -> dict[int, Job]:
    return {i: Job(id=i, name=n) for i, n in jobs.items()}

def job_id_by_name(jobs: dict[int, Job], name: str) -> int | None:
    for j in jobs.values():
        if j.name == name:
            return j.id
    return None


# Recommendations are constructed in two steps: first, infer the user's skill
# scores from his experiences, then, find out jobs that are relevant given the
# skill scores.

def job_recommendation(
        experiences_skills: "ExperiencesSkills",
        jobs_skills: "JobsSkills",
        experiences: list[ExperienceId],
        return_graph: bool,
        skill_centrality_measure: Callable[[nx.Graph], dict[SkillId, float]]
        ) -> "JobRecommendation":
    skill_scores, g = skills_from_experiences(experiences_skills, experiences,
                                              skill_centrality_measure)
    jobs = jobs_from_skills(jobs_skills, skill_scores)

    if return_graph:
        # Get connected subgraphs and lay them out separately so they don't
        # overlap.
        components: list[nx.Graph] = [
                g.subgraph(c).copy() #type:ignore
                for c in nx.connected_components(g)
                ]

        # Choose a number of columns and rows just big enough to fit all the
        # components.
        n_components = len(components)
        n = floor(sqrt(n_components))
        if n * n == n_components:
            n_row = n
            n_col = n
        elif n * (n + 1) > n_components:
            n_row = n
            n_col = n + 1
        else:
            n_row = n + 1
            n_col = n + 1

        centers = [(x, y) for y in range(n_row) for x in range(n_col)]

        layouts: list[dict[SkillId, npt.NDArray[np.float64]]] = [
                nx.kamada_kawai_layout(
                    c, # type:ignore
                    center = (x, y),
                    scale = 0.5,
                    )
                for (x, y), c in zip(centers, components)
                ]

        merged_layouts = {}
        for l in layouts:
            merged_layouts.update(l)

        sg = SkillGraph(
                graph=g,
                layout=merged_layouts, # type: ignore
                centrality=skill_scores.to_dict(), # type: ignore
                )
        jobs = lens.skill_graph.set(sg)(jobs)
    return jobs


@dataclass(frozen=True)
class JobRecommendation:
    scores: pa.Series

    skill_graph: Optional["SkillGraph"]

    def items(self) -> Iterable[tuple[JobId, float]]:
        return self.scores.items() # type: ignore


@dataclass(frozen=True)
class SkillGraph:
    graph: nx.Graph
    layout: dict[SkillId, npt.NDArray[np.float64]]
    centrality: dict[SkillId, np.float64]


# Each step relies on a distinct map: one relating experiences to skills and
# the other jobs to skills.  Each maps is encoded as a binary data frame where
# the rows represent jobs (resp. experiences) and the columns represent skills.

@dataclass(frozen=True)
class JobsSkills:
    df: pa.DataFrame


def mk_jobs_skills(df: pa.DataFrame) -> JobsSkills:
    return JobsSkills(df=df)


@dataclass(frozen=True)
class ExperiencesSkills:
    df: pa.DataFrame


def mk_experiences_skills(df: pa.DataFrame) -> ExperiencesSkills:
    return ExperiencesSkills(df=df)


# At the first step, we compute a user's skill centrality by constructing a
# skill graph and measuring each skills betweenness centrality in the graph.

def skills_from_experiences(
        experiences_skills: ExperiencesSkills,
        experiences: list[ExperienceId],
        skill_centrality_measure: Callable[[nx.Graph], dict[SkillId, float]]
        ) -> Tuple[pa.Series, nx.Graph]:
    g: nx.Graph = skill_graph(experiences_skills, experiences)
    scores: pa.Series = skill_scores(g, skill_centrality_measure)
    return scores, g

def skill_graph(
        experiences_skills: ExperiencesSkills,
        experiences: list[ExperienceId],
        ) -> nx.Graph:
    """The skill graph.

    Two skills are connected if they share a common experience, that is if both
    column have a 1 in the same row of matrix experiences_skills. An elements
    m[i,j] in the resulting matrix m is equal to the number of times the two
    corresponding experiences, experiences[i] and experiences[j] share a common
    experience.

    >>> experiences_skills = ExperiencesSkills(df=pa.DataFrame(
    ...     [[1, 0, 1],
    ...      [1, 0, 0],
    ...      [1, 1, 1]],
    ...     columns=["skill_1", "skill_2", "skill_3"],
    ...     index=[("exp_1", "pro"), ("exp_2", "pro"), ("exp_3", "perso")],
    ...     ))
    >>> selected_experiences = [
    ...     Experience(name="exp_1", exp_type="pro"),
    ...     Experience(name="exp_2", exp_type="pro"),
    ...     ]
    >>> g = skill_graph(experiences_skills, selected_experiences)
    >>> for edge in nx.generate_edgelist(g):
    ...     print(edge)
    Skill(name='skill_1') Skill(name='skill_1') {'weight': 2}
    Skill(name='skill_1') Skill(name='skill_3') {'weight': 1}
    Skill(name='skill_3') Skill(name='skill_3') {'weight': 1}
    """
    index = [x for x in experiences]
    selected_experiences: npt.NDArray[np.int32] = experiences_skills.df.loc[index, :].values
    positive_skills: pa.Series = selected_experiences.sum(axis=0) > 0
    selected_skills: list[SkillId] = [
            s for s in experiences_skills.df.columns[positive_skills]
            ]
    selected_experiences_skills = selected_experiences[:, positive_skills]
    adjacency_matrix = np.matmul(
            selected_experiences_skills.transpose(),
            selected_experiences_skills)
    g = nx.Graph(adjacency_matrix)
    g = nx.relabel_nodes(g, {i: x for i, x in enumerate(selected_skills)})
    return g


def skill_scores(
        g: nx.Graph,
        centrality_measure: Callable[[nx.Graph], dict[SkillId, float]],
                 ) -> pa.Series:
    """Betweenness centrality of each skill in the graph.

    >>> g = nx.Graph()
    >>> g.add_edge(1, 2))
    >>> g.add_edge(2), 3))
    >>> g.add_edge(1), 1))
    >>> g.add_edge(2), 2))
    >>> g.add_edge(3), 3))
    >>> skill_scores(g, lambda g: dict(nx.betweenness_centrality(g, endpoints=True))))
    1    0.666667
    2    1.000000
    3    0.666667
    dtype: float64
    >>> g = nx.Graph()
    >>> g.add_edge(1), 2))
    >>> g.add_edge(1), 3))
    >>> g.add_edge(2), 4))
    >>> g.add_edge(3), 4))
    >>> g.add_edge(4), 5))
    >>> skill_scores(g, lambda g: dict(nx.betweenness_centrality(g, endpoints=True)))
    1    0.45
    2    0.50
    3    0.50
    4    0.75
    5    0.40
    dtype: float64
    """
    centrality: dict[SkillId, float] = dict(centrality_measure(g)) # type:ignore
    return pa.Series({s: c  for s, c in centrality.items()})


# At the second step, we compute similarly the jobs scores by multiplying each
# column by the corresponding skill_score and taking the sum over the columns.
# The jobs with a score greater than 0 constitute the list of suggested jobs,
# sorted by descending score.

def jobs_from_skills(
        jobs_skills: JobsSkills,
        skill_scores: pa.Series,
        ) -> "JobRecommendation":
    job_scores: pa.Series = ((jobs_skills.df * skill_scores)
                              .sum(axis=1)
                              .sort_values(ascending=False))
    job_scores = job_scores.loc[job_scores > 0]
    return JobRecommendation(scores=job_scores, skill_graph=None)


