"""Logic in pure functions.
"""

from dataclasses import dataclass
from typing import Iterable, Iterator, Tuple
import pandas as pa


# The objective of this application is to make job recommendations based on an
# individual job experiences and skills.
# Jobs, experiences and skills are identified by their names. An experience
# also has a type, personal or professional.

@dataclass(frozen=True)
class Experience:
    name: str
    exp_type: str

@dataclass(frozen=True)
class Skill:
    name: str

@dataclass
class Job:
    name: str


# Recommendations are constructed in two steps: first, infer the user's skills
# from his experiences, then, find out jobs that are relevant given these
# skills.

def job_recommendation(
        experiences_skills: "ExperiencesSkills",
        jobs_skills: "JobsSkills",
        experiences: list[Experience],
        ) -> "JobRecommendation":
    skills = skills_from_experiences(experiences_skills, experiences)
    jobs = jobs_from_skills(jobs_skills, skills)
    return jobs


@dataclass(frozen=True)
class JobRecommendation:
    scores: pa.Series

    def items(self) -> Iterable[tuple[Job, float]]:
        return [(Job(name=str(n)), s) for n, s in self.scores.items()]


# Each step relies on a distinct map: one relating experiences to skills and
# the other jobs to skills.  Each maps is encoded as a binary data frame where
# the rows represent jobs (resp. experiences) and the columns represent skills.

@dataclass(frozen=True)
class JobsSkills:
    df: pa.DataFrame


def mk_jobs_skills(df: pa.DataFrame) -> JobsSkills:
    try:
        js = df.set_index("Métier")
    except KeyError:
        raise KeyError("The jobs_skills dataframe is missing the index column.")

    if js is None:
        raise ValueError("Expecting more columns in the jobs_skills data frame.")
    else:
        return JobsSkills(df=js)


def jobs(js: JobsSkills) -> list[Job]:
    ms: Iterator[str] = iter(js.df.index)
    return [Job(name=m) for m in ms]


def skills(js: JobsSkills) -> list[Skill]:
    cs: Iterator[str] = iter(js.df.columns)
    return [Skill(name=c) for c in cs]


@dataclass(frozen=True)
class ExperiencesSkills:
    df: pa.DataFrame


def mk_experiences_skills(df: pa.DataFrame) -> ExperiencesSkills:
    try:
        es = df.set_index(["Expérience", "type"])
    except KeyError:
        raise KeyError("The experiences_skills dataframe is missing the index columns.")

    if es is None:
        raise ValueError("Expecting more columns in the experiences_skills data frame.")
    else:
        return ExperiencesSkills(df=es)


def experiences(es: ExperiencesSkills) -> list[Experience]:
    ms: Iterator[Tuple[str, str]] = iter(es.df.index)
    return [Experience(name=m, exp_type=t) for m, t in ms]



# At the first step, we compute the skills scores by counting the number of
# times each skill is associated to an experience provided by the user through
# the experiences_skills map. We keep the skills that were selected at least
# once.

def skills_from_experiences(
        experiences_skills: ExperiencesSkills,
        experiences: list[Experience],
        ) -> set[Skill]:
    index = [(x.name, x.exp_type) for x in experiences]
    scores: pa.Series = experiences_skills.df.loc[index, :].sum(axis=0)
    scores = scores.loc[scores > 0]
    scores_names: Iterable[str] = iter(scores.index)
    return set(Skill(name=n) for n in scores_names)


# At the second step, we compute similarly the jobs scores by counting the
# number of times each job is associated to a selected skill by the
# jobs_skills map. The jobs with a score greater than 0 constitute the list of
# suggested jobs, sorted by descending score.

def jobs_from_skills(
        jobs_skills: JobsSkills,
        skills: set[Skill],
        ) -> "JobRecommendation":
    index = [c.name for c in skills]
    scores: pa.Series = jobs_skills.df.loc[:, index].sum(axis=1)
    scores = scores.loc[scores > 0].sort_values(ascending=False)
    return JobRecommendation(scores=scores)
