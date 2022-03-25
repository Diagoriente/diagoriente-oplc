from dataclasses import dataclass

from oplc.core import (
    ExperiencesSkills,
    JobsSkills,
    mk_experiences_skills,
    mk_jobs_skills,
)
from oplc.pipelines import (
    check_data,
    experiences_skills_data_source,
    jobs_skills_data_source,
    pull_source,
    load_data_frame,
)

@dataclass
class Model:
    experiences_skills: "ExperiencesSkills"
    jobs_skills: "JobsSkills"

def init() -> Model:
    m = Model(
        experiences_skills=mk_experiences_skills(
            load_data_frame(pull_source(
                experiences_skills_data_source,
                "experiences_skills"
                ))
            ),
        jobs_skills=mk_jobs_skills(
            load_data_frame(pull_source(
                jobs_skills_data_source,
                "jobs_skills"
                ))
            )
        )

    check_data(m.experiences_skills, m.jobs_skills)

    return m




model = init()
