"""Stateful functions operating on the model.

The functions here call functions in oplc.core with the current model state and
mutate model as necessary. They should contain as little logic as possible and
only perform model state read and write operations. All logic should go in
oplc.core.
"""

from dataclasses import dataclass

from lenses import lens
import oplc_model.model as core
from src import action
import oplc_etl.pipelines as etl

@dataclass
class Model:
    experiences_skills: core.ExperiencesSkills
    jobs_skills: core.JobsSkills
    jobs: dict[core.JobId, core.Job]
    skills: dict[core.SkillId, core.Skill]
    experiences: dict[core.ExperienceId, core.Experience]


def init() -> Model:
    return Model(
        experiences_skills=core.mk_experiences_skills(etl.experiences_skills()),
        jobs_skills=core.mk_jobs_skills(etl.jobs_skills()),
        jobs=core.mk_jobs(etl.jobs()),
        skills=core.mk_skills(etl.skills()),
        experiences=core.mk_experiences(etl.experiences()),
        )


def get() -> Model:
    global model
    return model


def present(act: action.Action) -> Model:
    global model

    if isinstance(act, action.DataFrameUpdate):
        set_es = lens.experiences_skills.set(
                core.mk_experiences_skills(act.experiences_skills_df))
        set_js = lens.jobs_skills.set(
                core.mk_jobs_skills(act.jobs_skills_df))

        m = model
        m = set_js(m)
        m = set_es(m)
        model = m

    else:
        pass

    return model


model: Model = init()
