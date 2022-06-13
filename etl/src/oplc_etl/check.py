from typing import Tuple, TypeVar


# The data must conform to some prerequisites

def check_data(experiences_skills: pa.DataFrame, jobs_skills: pa.DataFrame) -> None:

    # Experiences, jobs and skills must all be unique in the data sets

    T = TypeVar("T")
    def duplicate_values(values: list[T]) -> list[Tuple[T,int]]:
        counts = pa.Series(values).value_counts()
        res = counts.loc[counts > 1].to_list()
        return res

    experiences: list[str] = experiences_skills.index.to_list()
    dup = duplicate_values(experiences)
    assert len(dup) == 0, f"Found duplicated experiences in experiences_skills matrix: {dup}"

    skills: list[str] = experiences_skills.columns.to_list()
    dup = duplicate_values(skills)
    assert len(dup) == 0, f"Found duplicated skills in experiences_skills matrix: {dup}"

    jobs: list[str] = jobs_skills.index.to_list()
    dup = duplicate_values(jobs)
    assert len(dup) == 0, f"Found duplicated jobs in jobs_skills matrix: {dup}"

    skills: list[str] = jobs_skills.columns.to_list()
    dup = duplicate_values(skills)
    assert len(dup) == 0, f"Found duplicated skills in jobs_skills matrix: {dup}"



