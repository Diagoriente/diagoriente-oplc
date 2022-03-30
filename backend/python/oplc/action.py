"""Actions given as input to the model.

These function take data in and return data that is fed to the model.present
function to trigger a model update.
"""

from dataclasses import dataclass
from oplc.pipelines import (
        experiences_skills_data_source,
        jobs_skills_data_source,
        pull_source,
        load_data_frame,
        )
import pandas as pa
from typing import Union

@dataclass
class NoAction:
    pass


@dataclass
class DataFrameUpdate:
    experiences_skills_df: pa.DataFrame
    jobs_skills_df: pa.DataFrame


def pull_data_source() -> DataFrameUpdate:
    es_csv = pull_source(
            experiences_skills_data_source,
            "experiences_skills",
            skip_if_exists=False)
    js_csv = pull_source(
            jobs_skills_data_source,
            "jobs_skills",
            skip_if_exists=False)

    es_df = load_data_frame(es_csv)
    js_df = load_data_frame(js_csv)
    return DataFrameUpdate(
            experiences_skills_df=es_df,
            jobs_skills_df=js_df,
            )

Action = Union[
        NoAction,
        DataFrameUpdate,
        ]

