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


Skills = NewType("Skills", pa.DataFrame)


def mk_skills(skills: pa.DataFrame) -> Skills:
    # We're just wrapping the dataframe in a newtype, but ideally we would check
    # the DataFrame column types if the pandas DataFrame type allowed
    # typechecking
    return Skills(skills)


Jobs = NewType("Jobs", pa.DataFrame)


def mk_jobs(jobs: pa.DataFrame) -> Jobs:
    return Jobs(jobs)


Sectors = NewType("Sectors", pa.DataFrame)


def mk_sectors(sectors: pa.DataFrame) -> Sectors:
    return Sectors(sectors)


JobsSkills = NewType("JobsSkills", pa.DataFrame)


def mk_jobs_skills(df: pa.DataFrame) -> JobsSkills:
    return JobsSkills(df)


SkillCooccurrence = NewType("SkillCooccurrence", pa.DataFrame)


def skill_cooccurrence(jobs_skills: JobsSkills) -> "SkillCooccurrence":
    skills_jobs = jobs_skills.transpose()
    # Remove skills that are not associated to any job
    # skills_jobs = skills_jobs.loc[skills_jobs.sum(axis=1) > 0, :]

    return SkillCooccurrence(skills_jobs.dot(skills_jobs.transpose()))


IndividualExperiences = NewType("IndividualExperiences", pa.DataFrame)
ExperienceWeights = NewType("ExperienceWeights", pa.DataFrame)
IndivSkills = NewType("IndivSkills", pa.DataFrame)

def mk_individual_experiences(
        job_id: npt.NDArray[int],
        begin: npt.NDArray[float],
        end: npt.NDArray[float],
        ) -> IndividualExperiences:
    return IndividualExperiences(pa.DataFrame({
        "job_id": job_id,
        "begin": begin,
        "end": end,
        }))


@dataclass
class Model:
    experiences: ExperienceWeights
    skills: IndivSkills
    main_job: int
    main_sector: int
    level: int


def model(
        indiv_exp: IndividualExperiences,
        jobs: Jobs,
        jobs_skills: JobsSkills,
        ) -> Model:

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
        "weight": (jobs_skills.loc[exp_weight.job_id, :]
                  .set_index(exp_weight.index)
                  .mul(exp_weight.weight, axis="index")
                  .sum()
                  ),
        })

    indiv_main_job = exp_weight.loc[lambda x: x.weight.idxmax(), "job_id"]
    indiv_main_sector = jobs.loc[indiv_main_job, "sector"]
    indiv_level = jobs.loc[exp_weight.job_id, "level"].max()

    return Model(
            experiences=ExperienceWeights(exp_weight),
            skills=IndivSkills(indiv_skills),
            main_job=indiv_main_job,
            main_sector=indiv_main_sector,
            level=indiv_level,
            )




@dataclass
class JobAccessibility:
    job_accessibility: pa.DataFrame
    skill_contribution: pa.DataFrame
    skill_gap: pa.DataFrame
    level_diff_weights: pa.Series


def job_accessibility(
        model: Model,
        jobs: Jobs,
        jobs_skills: JobsSkills,
        same_sector_first: bool,
        hide_practiced_jobs: bool,
        weigh_by_level_diff: bool,
        show_level_min: int,
        show_level_max: int,
        ) -> JobAccessibility:

    norm_job = np.sqrt((jobs_skills ** 2).sum(axis=1))
    norm_indiv = np.sqrt((model.skills.weight ** 2).sum())

    skill_contribution = (
            jobs_skills
            .mul(model.skills.weight, axis="columns")
            .div(norm_job * norm_indiv, axis="index")
            )

    job_access = skill_contribution.sum(axis=1)
    job_access = job_access.sort_values(ascending=False)


    if weigh_by_level_diff:
        lvl_diff_weight = 1 - (jobs.loc[job_access.index, "level"] - model.level) / 8
        lvl_diff_weight.loc[lvl_diff_weight > 1] = 1
        job_access = job_access * lvl_diff_weight

    if hide_practiced_jobs:
        job_access = job_access.drop(model.experiences.job_id)

    job_access = job_access.loc[
            (jobs.loc[job_access.index, "level"] >= show_level_min) 
            & (jobs.loc[job_access.index, "level"] <= show_level_max)
            ]

    if same_sector_first:
        select_same_sector = jobs.sector == model.main_sector
        same_sector_jobs = job_access.loc[select_same_sector].sort_values(ascending=False)
        other_sectors_jobs = job_access.loc[~select_same_sector].sort_values(ascending=False)
        job_access = pa.concat([same_sector_jobs, other_sectors_jobs])

    skill_contribution_normalized = (
            skill_contribution
            .div(skill_contribution.sum(axis=1), axis="index")
            .loc[job_access.index, :]
            )

    scaled_skill = model.skills.weight / model.skills.weight.max()
    skill_gap = (
            (jobs_skills.loc[job_access.index, :] - scaled_skill) 
            * jobs_skills.loc[job_access.index, :]
            )

    return JobAccessibility(
            job_accessibility=job_access,
            skill_contribution=skill_contribution_normalized, 
            skill_gap=skill_gap,
            level_diff_weights=lvl_diff_weight if weigh_by_level_diff else None,
            )


@dataclass
class SkillAccessibility:
    skill_accessibility: pa.DataFrame
    skill_contribution: pa.DataFrame


def skill_accessibility(
        model: Model,
        skill_cooc: SkillCooccurrence,
        ) -> SkillAccessibility:

    mask = pa.DataFrame(np.ones(skill_cooc.shape),
                        index=skill_cooc.index,
                        columns=skill_cooc.columns)
    for i,j in zip(skill_cooc.index, skill_cooc.index):
        mask.loc[i,j] = 0

    skill_cooc = skill_cooc * mask

    norm_skill = np.sqrt((skill_cooc ** 2).sum(axis=1))
    norm_indiv = np.sqrt((model.skills.weight ** 2).sum())

    skill_contribution = (
            skill_cooc
            .mul(model.skills.weight, axis="columns")
            .div(norm_skill * norm_indiv, axis="index")
            )

    skill_access = skill_contribution.sum(axis=1)
    skill_access = skill_access.sort_values(ascending=False)

    skill_contribution_normalized = (
            skill_contribution.div(skill_contribution.sum(axis=1), axis="index")
            )
    skill_contribution_normalized.loc[skill_access.index, :]

    scaled_skill = model.skills.weight / model.skills.weight.max()
    skill_gap = (skill_cooc - scaled_skill) * skill_cooc

    return SkillAccessibility(
            skill_accessibility=skill_access,
            skill_contribution=skill_contribution_normalized,
            )


def job_accessibility_derivative(
        model: Model,
        jobs_skills: JobsSkills,
        ):
    r"""
    Job accessibility sensitivity to skill variation. Returns the partial 
    derivative of each job accessibility with respect to skill s_i:

    .. math::
        \frac{d}{d_{s_i}}
        \frac{1}{n_j}
        \sum_{\vec j} \frac{\vec j \cdot \vec s}{\lvert \vec j \rvert \lvert \vec s \rvert}

    where n_j is the number of jobs, \vec j a job vector and \vec s the user
    skill vector, j_i and s_i are the value for skill i respectively for the
    job \vec j and the user skills \vec s.

    Computing the derivative gives:

    .. math::

        \frac{1}{n_j}
        \sum_{\vec j}
        \frac{1}{\lvert \vec j \rvert}
        \left(
            \frac{j_i}{\left| \vec s \right|}
            -
            \frac{s_i \sum_i' j_i s_i}{\left| \vec s \right|^3}
        \right)

    """

    norm_job = np.sqrt((jobs_skills ** 2).sum(axis=1))
    norm_skills = np.sqrt((model.skills.weight ** 2).sum())

    # Dot product of each job vector and the individual's skill vector
    job_dot_skill = (
            jobs_skills
            .mul(model.skills.weight, axis="columns")
            .sum(axis="columns")
            )

    job_accessibility_derivative = pa.DataFrame(
            np.empty((len(model.skills), len(jobs_skills))),
            index = model.skills.index,
            columns = jobs_skills.index,
            )

    # Compute the derivative for each individual skill
    for i in model.skills.index:
        s_i = model.skills.weight.loc[i]
        j_i = jobs_skills.loc[:, i]

        job_accessibility_derivative.loc[i, :] = (
                (j_i / norm_skills)
                 - (s_i * job_dot_skill / (norm_skills ** 3))
        )

    return job_accessibility_derivative



@dataclass
class SkillPotential:
    per_job: pa.DataFrame
    average: pa.Series

def skill_potential(
        model: Model,
        jobs_skills: JobsSkills,
        job_accessibility: JobAccessibility,
        weigh_by_level_diff: bool,
        weigh_by_job_accessibility: bool,
        ):

    per_job = job_accessibility_derivative(model, jobs_skills)

    # Compute the derivative for each individual skill
    for i in model.skills.index:
        s_i = model.skills.weight.loc[i]
        j_i = jobs_skills.loc[:, i]


        if weigh_by_level_diff:
            per_job.loc[i, :] = (
                    per_job.loc[i, :]
                    * job_accessibility.level_diff_weights
                    )

        if weigh_by_job_accessibility:
            per_job.loc[i, :] = (
                    per_job.loc[i, :]
                    * job_accessibility.job_accessibility
                    )

    average = per_job.mean(axis="columns").sort_values(ascending=False)

    per_job = per_job.loc[average.index, :]

    return SkillPotential(per_job=per_job, average=average)
