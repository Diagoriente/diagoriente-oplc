import pandas as pa
from typing import Tuple, TypeVar
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Union, Literal
from oplc.config import (
        DATASET_CACHE_DIR, EXPERIENCES_SKILLS_DATA_SOURCES,
        JOBS_SKILLS_DATA_SOURCES,
        )
from oplc.model import DataSet

# There are two kinds of data pieces: the experiences_skills map and
# jobs_skills map.

DataPieceKind = Literal["experiences_skills", "jobs_skills"]

# Each piece of data is stored locally as a csv file. Different versions are
# stored with different filenames.

@dataclass(frozen=True)
class LocalCsv:
    kind: DataPieceKind
    date: datetime
    name: str

def local_csv_dir(kind: DataPieceKind) -> Path:
    return DATASET_CACHE_DIR / "local_csv" / kind

def local_csv_path(kind: DataPieceKind) -> Path:
    return local_csv_dir(kind) / "content.csv"

def local_csv_path_meta(kind: DataPieceKind) -> Path:
    return local_csv_dir(kind) / "meta.json"

# A data source defines where to fetch a data piece, like a local csv file or a
# remote google docs spreadsheet.

DataSource = Union["LocalSourceCsv", "GoogleDocsCsv"]

@dataclass(frozen=True)
class LocalSourceCsv:
    name: str
    path: Path

# A google docs spreadsheet is identified by a key and gid that can be seen in
# the url when browsing the spreadsheet. For example, if the url is
# https://docs.google.com/spreadsheets/d/1PCLOHAE0yXt_tghVlV44ZTt7ZzEUV-f3COrKEMbLamc/edit?pli=1#gid=0
# The key is 1PCLOHAE0yXt_tghVlV44ZTt7ZzEUV-f3COrKEMbLamc and the gid is 0.

@dataclass(frozen=True)
class GoogleDocsCsv:
    name: str
    key: str
    gid: str

    def url(self) -> str:
        return f"https://docs.google.com/spreadsheets/d/{self.key}/export?gid={self.gid}&format=csv"

    # The data is cached locally.

    def cache_path(self) -> Path:
        return DATASET_CACHE_DIR / Path(f"google_sheet_{self.key}_{self.gid}.csv")


# Each piece of data has a single data source. The sources are defined in
# oplc.config.

def data_source_from_def(definition: dict[str, str]) -> DataSource:
    if definition["type"] == "google docs":
        return GoogleDocsCsv(
                name=definition["name"],
                key=definition["key"],
                gid=definition["gid"])

    else:
        return LocalSourceCsv(
                name=definition["name"],
                path=Path(definition["path"])
                )


# Each data piece have its source and local csv.

experiences_skills_data_source = data_source_from_def(
        EXPERIENCES_SKILLS_DATA_SOURCES
        )

jobs_skills_data_source = data_source_from_def(
        JOBS_SKILLS_DATA_SOURCES
        )


# The data must conform to some prerequisites

def check_data(ds: DataSet) -> None:

    # Experiences, jobs and skills must all be unique in the data sets

    T = TypeVar("T")
    def duplicate_values(values: list[T]) -> list[Tuple[T,int]]:
        counts = pa.Series(values).value_counts()
        counts = counts.loc[counts > 1]
        return list(counts.items())

    dup = duplicate_values(ds.experiences_skills.df.index.to_list())
    assert len(dup) == 0, f"Found duplicated experiences in experiences_skills matrix: {dup}"

    dup = duplicate_values(ds.experiences_skills.df.columns.to_list())
    assert len(dup) == 0, f"Found duplicated skills in experiences_skills matrix: {dup}"

    dup = duplicate_values(ds.jobs_skills.df.index.to_list())
    assert len(dup) == 0, f"Found duplicated jobs in jobs_skills matrix: {dup}"

    dup = duplicate_values(ds.jobs_skills.df.columns.to_list())
    assert len(dup) == 0, f"Found duplicated skills in jobs_skills matrix: {dup}"


    # Data must be boolean
