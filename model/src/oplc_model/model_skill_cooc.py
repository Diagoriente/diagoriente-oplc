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


SkillCooccurrence = NewType("SkillCooccurrence", pa.DataFrame)


def skill_cooccurrence(jobs_skills: JobsSkills) -> "SkillCooccurrence":
    skills_jobs = jobs_skills.df.transpose()
    # Remove skills that are not associated to any job
    # skills_jobs = skills_jobs.loc[skills_jobs.sum(axis=1) > 0, :]

    return SkillCooccurrence(skills_jobs.dot(skills_jobs.transpose()))


IndividualExperiences = NewType("IndividualExperiences", pa.DataFrame)
ExperienceWeights = NewType("ExperienceWeights", pa.DataFrame)
IndivSkills = NewType("IndivSkills", pa.DataFrame)

def mk_individual_experiences(
        job_id: npt.NDArray[JobId],
        begin: npt.NDArray[float],
        end: npt.NDArray[float],
        ) -> IndividualExperiences:
    return IndividualExperiences(pa.DataFrame({
        "job_id": job_id,
        "begin": begin,
        "end": end,
        }))


def experience_weights(
        indiv_exp: IndividualExperiences,
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
        exp_weight.loc[i, "recency"] = year_recency[-1]
        exp_weight.loc[i, "weight"] = experience_weight


    # Multiply each experience skill (row) vector by the corresponding
    # experience weight and sum the results
    indiv_skills = pa.DataFrame({
        "weight": (jobs_skills.df.loc[exp_weight.job_id, :]
                  .set_index(exp_weight.index)
                  .mul(exp_weight.weight, axis="index")
                  .sum()
                  ),
        })

    return ExperienceWeights(exp_weight), IndivSkills(indiv_skills)


JobAccessibility = NewType("JobAccessibility", pa.DataFrame)
SkillContribution = NewType("SkillContribution", pa.DataFrame)


def job_accessibility(
        jobs_skills: JobsSkills,
        indiv_skills: IndivSkills,
        ) -> JobAccessibility:

    norm_job = np.sqrt((jobs_skills.df ** 2).sum(axis=1))
    norm_indiv = np.sqrt((indiv_skills.weight ** 2).sum())

    skill_contribution = (
            jobs_skills.df
            .mul(indiv_skills.weight, axis="columns")
            .div(norm_job * norm_indiv, axis="index")
            )

    job_access = skill_contribution.sum(axis=1)
    job_access = job_access.sort_values(ascending=False)

    skill_contribution_normalized = (
            skill_contribution.div(skill_contribution.sum(axis=1), axis="index")
            )
    skill_contribution_normalized.loc[job_access.index, :]

    scaled_skill = indiv_skills.weight / indiv_skills.weight.max()
    skill_gap = (jobs_skills.df - scaled_skill) * jobs_skills.df

    return job_access, skill_contribution_normalized, skill_gap


SkillAccessibility = NewType("SkillAccessibility", pa.DataFrame)


def skill_accessibility(
        skill_cooc: SkillCooccurrence,
        indiv_skills: IndivSkills,
        ) -> SkillAccessibility:

    mask = pa.DataFrame(np.ones(skill_cooc.shape),
                        index=skill_cooc.index,
                        columns=skill_cooc.columns)
    for i,j in zip(skill_cooc.index, skill_cooc.index):
        mask.loc[i,j] = 0

    skill_cooc = skill_cooc * mask

    norm_skill = np.sqrt((skill_cooc ** 2).sum(axis=1))
    norm_indiv = np.sqrt((indiv_skills.weight ** 2).sum())

    skill_contribution = (
            skill_cooc
            .mul(indiv_skills.weight, axis="columns")
            .div(norm_skill * norm_indiv, axis="index")
            )

    skill_access = skill_contribution.sum(axis=1)
    skill_access = skill_access.sort_values(ascending=False)

    skill_contribution_normalized = (
            skill_contribution.div(skill_contribution.sum(axis=1), axis="index")
            )
    skill_contribution_normalized.loc[skill_access.index, :]

    scaled_skill = indiv_skills.weight / indiv_skills.weight.max()
    skill_gap = (skill_cooc - scaled_skill) * skill_cooc

    return skill_access, skill_contribution_normalized


def job_accessibility_from_experiences(
        indiv_exp: IndividualExperiences,
        jobs_skills: JobsSkills,
        ) -> tuple[ExperienceWeights, IndivSkills, JobAccessibility, SkillContribution]:

    exp_w, indiv_skills = experience_weights(
        indiv_exp=indiv_exp,
        jobs_skills=jobs_skills,
    )

    job_access, skill_contrib, skill_gap = job_accessibility(jobs_skills, indiv_skills)

    return exp_w, indiv_skills, job_access, skill_contrib, skill_gap
