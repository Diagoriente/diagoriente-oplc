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
    jobs: dict[core.JobId, core.Job]
    skills: dict[core.SkillId, core.Skill]
    experiences: dict[core.ExperienceId, core.Experience]


def init() -> Model:
    experiences_skills_df = load_data_frame(pull_source(
                experiences_skills_data_source,
                "experiences_skills"
                ))
    jobs_skills_df = load_data_frame(pull_source(
                jobs_skills_data_source,
                "jobs_skills"
                ))

    # TODO
    # check_data(experiences_skills_df, jobs_skills_df)

    jobs = {i: core.Job(id=i, name=j) # type:ignore
            for i, j in enumerate(
                            jobs_skills_df.loc[:, "Métier"], # type:ignore
                            )
            }
    skills = {i: core.Skill(id=i, name=s)
              for i, s in enumerate(
                  jobs_skills_df.drop(columns=["Métier"])
                  .columns # type:ignore
                  )
              }
    experiences = {
            i: core.Experience(
                id=i,
                name=exp, # type:ignore
                exp_type=exp_type, # type:ignore
                )
            for i, (exp, exp_type) in enumerate(
                experiences_skills_df.loc[:, ["Expérience", "type"]].values # type:ignore
                )
            }

    skill_ids = list(range(len(skills)))

    experiences_skills_mat = (experiences_skills_df
                             .loc[:, [skills[s].name for s in skill_ids]]
                             .rename(
                                columns={x.name: i for i, x in skills.items()}
                                )
                             )

    jobs_skills_mat = (jobs_skills_df
                      .loc[:, [skills[s].name for s in skill_ids]]
                      .rename(
                          columns={x.name: i for i, x in skills.items()}
                          )
                      )

    m = Model(
        experiences_skills=core.mk_experiences_skills(
            experiences_skills_mat, # type:ignore
            ),
        jobs_skills=core.mk_jobs_skills(
            jobs_skills_mat, # type:ignore
            ),
        jobs=jobs,
        skills=skills,
        experiences=experiences,
        )

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
