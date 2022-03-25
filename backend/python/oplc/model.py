"""Stateful functions operating on the model.

The functions here call functions in oplc.core with the current model state and
mutate model as necessary. They should contain as little logic as possible and
only perform model state read and write operations. All logic should go in
oplc.core.
"""

from dataclasses import dataclass

from lenses import lens
from oplc import core
from oplc.pipelines import (
    check_data,
    experiences_skills_data_source,
    jobs_skills_data_source,
    pull_source,
    load_data_frame,
)
import oplc.action as act

@dataclass
class Model:
    experiences_skills: core.ExperiencesSkills
    jobs_skills: core.JobsSkills


def init() -> Model:
    m = Model(
        experiences_skills=core.mk_experiences_skills(
            load_data_frame(pull_source(
                experiences_skills_data_source,
                "experiences_skills"
                ))
            ),
        jobs_skills=core.mk_jobs_skills(
            load_data_frame(pull_source(
                jobs_skills_data_source,
                "jobs_skills"
                ))
            )
        )

    check_data(m.experiences_skills, m.jobs_skills)

    return m


def get() -> Model:
    global model
    return model


def present(action: act.Action) -> Model:
    global model

    if isinstance(action, act.DataFrameUpdate):
        set_es = lens.experiences_skills.set(
                core.mk_experiences_skills(action.experiences_skills_df))
        set_js = lens.jobs_skills.set(
                core.mk_jobs_skills(action.jobs_skills_df))

        m = model
        m = set_js(m)
        m = set_es(m)
        model = m

    else:
        pass

    return model


model: Model = init()
