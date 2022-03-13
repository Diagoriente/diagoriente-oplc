from dataclasses import dataclass
from pathlib import Path
from typing import Union
from oplc.constants import DATASET_CACHE_DIR
import pandas as pa
from typing import Iterable


@dataclass(frozen=True)
class LocalCsv:
    name: str
    path: Path


@dataclass(frozen=True)
class GoogleDocsCsv:
    name: str
    key: str
    gid: str

    def url(self) -> str:
        return f"https://docs.google.com/spreadsheets/d/{self.key}/export?gid={self.gid}&format=csv"

    def cache_path(self) -> Path:
        return DATASET_CACHE_DIR / Path(f"google_sheet_{self.key}_{self.gid}.csv")


DataSet = Union[LocalCsv, GoogleDocsCsv]


@dataclass
class Metier:
    name: str


@dataclass(frozen=True)
class Competence:
    name: str


@dataclass(frozen=True)
class CompetencesMetiers:
    df: pa.DataFrame

    def metiers(self) -> list[Metier]:
        ms: Iterable[str] = self.df.index
        return [Metier(name=m) for m in ms]

    def competences(self) -> list[Competence]:
        cs: Iterable[str] = self.df.columns
        return [Competence(name=c) for c in cs]



@dataclass(frozen=True)
class Model:
    competences_metiers: dict[DataSet, CompetencesMetiers]
    data_sets: dict[str, DataSet]

