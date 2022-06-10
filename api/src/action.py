"""Actions given as input to the model.

These function take data in and return data that is fed to the model.present
function to trigger a model update.
"""

from dataclasses import dataclass
import oplc_etl.pipelines
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
    es_df = oplc_etl.pipelines.experiences_skills_df(skip_if_exists=False)
    js_df = oplc_etl.pipelines.jobs_skills_df(skip_if_exists=False)
    return DataFrameUpdate(
            experiences_skills_df=es_df, # type: ignore
            jobs_skills_df=js_df, # type: ignore
            )

Action = Union[
        NoAction,
        DataFrameUpdate,
        ]

