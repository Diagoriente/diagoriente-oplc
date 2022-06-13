import pandas as pa
import requests
from requests.exceptions import HTTPError
from datetime import datetime
import json
import logging
import pandas as pa
from typing import Tuple, TypeVar
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Union, Literal

DATASET_CACHE_DIR = Path("/tmp/diagoriente-oplc/cache/data_set/")

EXPERIENCES_SKILLS_DATA_SOURCES = {
    "type": "google docs",
    "name": "Base de données proto orientation par les compétences - Expériences",
    "key": "1PCLOHAE0yXt_tghVlV44ZTt7ZzEUV-f3COrKEMbLamc",
    "gid": "0",
}

JOBS_SKILLS_DATA_SOURCES = {
    "type": "google docs",
    "name": "Base de données proto orientation par les compétences - Métiers",
    "key": "1PCLOHAE0yXt_tghVlV44ZTt7ZzEUV-f3COrKEMbLamc",
    "gid": "1032477800",
}


# There are two kinds of data pieces: the experiences_skills map and
# jobs_skills map.

DataPieceKind = Literal["experiences_skills", "jobs_skills"]

# Each piece of data is stored locally as a csv file. Different versions are
# stored with different filenames.

@dataclass
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

@dataclass
class LocalSourceCsv:
    name: str
    path: Path

# A google docs spreadsheet is identified by a key and gid that can be seen in
# the url when browsing the spreadsheet. For example, if the url is
# https://docs.google.com/spreadsheets/d/1PCLOHAE0yXt_tghVlV44ZTt7ZzEUV-f3COrKEMbLamc/edit?pli=1#gid=0
# The key is 1PCLOHAE0yXt_tghVlV44ZTt7ZzEUV-f3COrKEMbLamc and the gid is 0.

@dataclass
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



def pull_source(
        ds: DataSource,
        kind: DataPieceKind,
        skip_if_exists: bool=True
        ) -> LocalCsv:

    if not local_csv_dir(kind).exists() or skip_if_exists == False:
        logging.info(f'Pulling data source "{ds.name}"')

        if isinstance(ds, GoogleDocsCsv):
            # TODO: switch to an asynchronous HTTP request (httpx, aiohttp)
            res = requests.get(ds.url())
            res.encoding = "utf-8"

            try:
                res.raise_for_status()
            except HTTPError:
                raise HTTPError(f"Couldn't download Google docs spreadsheet with key {ds.key} and gid {ds.gid}")

            content: str = res.text

        else:
            with open(ds.path, "r") as f:
                content = f.read()

        local_csv_dir(kind).mkdir(parents=True, exist_ok=True)

        with open(local_csv_path(kind), "w") as f:
            f.write(content)

        with open(local_csv_path_meta(kind), "w") as f:
            f.write(json.dumps({
                    "kind": kind,
                    "date": datetime.utcnow().isoformat(),
                    "name": ds.name,
                  }))
    else:
        logging.info(f'Using local csv in "{local_csv_dir(kind)}"')

    return load_local_csv(kind)


def load_local_csv(kind: DataPieceKind):
    with open(local_csv_path_meta(kind), "r") as f:
        meta = json.loads(f.read())
        return LocalCsv(
                kind=kind,
                date=datetime.fromisoformat(meta["date"]),
                name=meta["name"]
                )


def load_data_frame(ds: LocalCsv) -> pa.DataFrame :
    return pa.DataFrame(pa.read_csv(local_csv_path(ds.kind)))


def experiences_skills_df():
    return load_data_frame(pull_source(
            experiences_skills_data_source,
            "experiences_skills",
            ))


def jobs_skills_df() -> pa.DataFrame:
    return load_data_frame(pull_source(
            jobs_skills_data_source,
            "jobs_skills"
            ))


def jobs() -> dict[int, str]:
    return {i: j # type:ignore
        for i, j in enumerate(
                        jobs_skills_df().loc[:, "Métier"], # type:ignore
                        )
        }


def skills() -> dict[int, str]:
    return {i: s
          for i, s in enumerate(
              jobs_skills_df().drop(columns=["Métier"])
              .columns # type:ignore
              )
          }


def skill_ids() -> list[int]:
    return list(range(len(skills())))


def experiences() -> dict[int, tuple[str, str]]:
    return {i: (exp, exp_type)
            for i, (exp, exp_type) in enumerate(
                experiences_skills_df().loc[:, ["Expérience", "type"]].values # type:ignore
                )
            }


def experiences_skills() -> pa.DataFrame:
    skills_ = skills()
    return (experiences_skills_df()
            .loc[:, [skills_[s] for s in skill_ids()]]
            .rename(
               columns={x: i for i, x in skills_.items()}
               )
            )


def jobs_skills() -> pa.DataFrame:
    skills_ = skills()
    return (jobs_skills_df()
            .loc[:, [skills_[s] for s in skill_ids()]]
            .rename(
                columns={x: i for i, x in skills_.items()}
                )
            )

def get_data():
    return jobs(), skills(), experiences(), experiences_skills(), jobs_skills()
