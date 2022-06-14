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

SkillId = int

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


@dataclass(frozen=True)
class JobsSkills:
    df: pa.DataFrame


def mk_jobs_skills(df: pa.DataFrame) -> JobsSkills:
    return JobsSkills(df=df)


@dataclass(frozen=True)
class SkillCooccurrence:
    df: pa.DataFrame


def skill_cooccurrence(jobs_skills: JobsSkills) -> "SkillCooccurrence":
    skills_jobs = jobs_skills.df.transpose()
    # Remove skills that are not associated to any job
    # skills_jobs = skills_jobs.loc[skills_jobs.sum(axis=1) > 0, :]

    return skills_jobs.dot(skills_jobs.transpose())


ExperienceWeights = NewType("ExperienceWeights", pa.DataFrame)
IndivSkills = NewType("IndivSkills", pa.DataFrame)


def experience_weights(
        indiv_exp: pa.DataFrame,
        jobs: dict[int, Job],
        jobs_skills: JobsSkills,
        ) -> tuple[ExperienceWeights, IndivSkills]:

    exp_weight = pa.DataFrame({
        "job_id": indiv_exp.loc[:, "job_id"],
        "begin": indiv_exp.loc[:, "begin"],
        "end": indiv_exp.loc[:, "end"],
        "duration": np.empty(len(indiv_exp), dtype=float),
        "recency": np.empty(len(indiv_exp), dtype=float),
        "weight": np.empty(len(indiv_exp), dtype=float),
        })

    today = datetime.today()

    for i in exp_weight.index:
        begin = pa.to_datetime(exp_weight.loc[i, "begin"])
        end = pa.to_datetime(exp_weight.loc[i, "end"])
        years = list(range(begin.year, end.year + 1))
        start_day_per_year = (
                [begin]
                + [datetime(year=y, month=1, day=1) for y in years[1:]]
                )
        end_day_per_year = (
                [datetime(year=y, month=12, day=31) for y in years[:-1]]
                + [end]
                )
        days_per_year = [(datetime(year=y+1, month=1, day=1) - datetime(year=y, month=1, day=1)).days 
                          for y in years]
        # Proportion of year worked for each year
        year_proportion = [((e - s).days + 1) / d
                           for s,e,d
                           in zip(start_day_per_year, end_day_per_year, days_per_year)]
        # Experience recency per year
        year_recency = [(today - e).days / d for d, e in zip(days_per_year, end_day_per_year)]

        year_weight = [p / (r + 1) for p, r in zip(year_proportion, year_recency)]

        experience_weight = sum(year_weight)

        exp_weight.loc[i, "duration"] = sum(year_proportion)
        exp_weight.loc[i, "rencency"] = year_recency[-1]
        exp_weight.loc[i, "weight"] = experience_weight


    # Multiply each experience skill (row) vector by the corresponding
    # experience weight and sum the results
    indiv_skills = pa.DataFrame({
        "weight": (jobs_skills.df.loc[exp_weight.experience_id, :]
                  .set_index(exp_weight.index)
                  .mul(exp_weight.weight, axis="index")
                  .sum()
                  ),
        })

    return ExperienceWeights(exp_weight), IndivSkills(indiv_skills)


JobDistance = NewType("JobDistance", pa.DataFrame)


def job_distance(
        jobs_skills: JobsSkills,
        indiv_skills: IndivSkills,
        metric: str,
        ) -> JobDistance:
    dist_job = pa.Series(np.empty(jobs_skills.df.shape[0]),
                          index=jobs_skills.df.index,
                         )

    for j in jobs_skills.df.index:
        dist_job.loc[j] = pdist([indiv_skills.loc[jobs_skills.df.columns].weight,
                                 jobs_skills.df.loc[j, :],
                                 ],
                                 metric=metric)

    return JobDistance(dist_job.sort_values())
