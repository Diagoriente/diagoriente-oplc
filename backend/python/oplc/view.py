from pydantic import BaseModel

from oplc.constants import DEFAULT_DATA_SET
from oplc.model import DataSet, Metier, Competence

from typing import Callable, TypeVar

T = TypeVar('T')
U = TypeVar('U')
View = Callable[[T], U]


class MetierJson(BaseModel, frozen=True):
    name: str

    @staticmethod
    def view(m: Metier) -> "MetierJson":
        return MetierJson.construct(name=m.name)


class CompetenceJson(BaseModel, frozen=True):
    name: str

    @staticmethod
    def view(m: Competence) -> "CompetenceJson":
        return CompetenceJson(name=m.name)



class DataSetJson(BaseModel):
    name: str

    @staticmethod
    def view(ds: DataSet) -> "DataSetJson":
        return DataSetJson(name=ds.name)


class DataSetsJson(BaseModel):
    default: str
    datasets: list[str]

    @staticmethod
    def view(dss: dict[str, DataSet]) -> "DataSetsJson":
        return DataSetsJson(default=DEFAULT_DATA_SET,
                            datasets=[ds.name for ds in dss.values()])


class MetiersJson(BaseModel):
    metiers: list[MetierJson]

    @staticmethod
    def view(metiers: list[Metier]) -> "MetiersJson":
        return MetiersJson(metiers=[MetierJson.view(m)
            for m in metiers])


class CompetencesJson(BaseModel):
    competences: list[CompetenceJson]

    @staticmethod
    def view(competences: list[Competence]) -> "CompetencesJson":
        return CompetencesJson(
                competences=[CompetenceJson.view(c)
                    for c in competences])
