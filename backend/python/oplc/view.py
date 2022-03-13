from pydantic import BaseModel

from oplc.constants import DEFAULT_DATA_SET
from oplc.model import Model, DataSet, Metier, Competence, CompetencesMetiers

from typing import Callable, TypeVar, Any, Tuple

I = TypeVar('I')
E = TypeVar('E')
T = TypeVar('T')
U = TypeVar('U')
View = Callable[[I, E, T], U]


class MetierJson(BaseModel, frozen=True):
    name: str

    @staticmethod
    def view_metier(_: Any, __: Any, m: Metier) -> "MetierJson":
        return MetierJson.construct(name= m.name)


class CompetenceJson(BaseModel, frozen=True):
    name: str

    @staticmethod
    def view_competence(_: Any, __: Any, m: Competence) -> "CompetenceJson":
        return CompetenceJson(name=m.name)



class DataSetJson(BaseModel):
    name: str

    @staticmethod
    def view_data_set(_: Any, __: Any, ds: DataSet) -> "DataSetJson":
        return DataSetJson(name=ds.name)


class DataSetsJson(BaseModel):
    default: str
    datasets: list[str]

    @staticmethod
    def view_data_sets(_: Any, __: Any, dss: list[DataSet]) -> "DataSetsJson":
        return DataSetsJson(default=DEFAULT_DATA_SET,
                            datasets=[ds.name for ds in dss])

    @staticmethod
    def view_model(_: Any, __: Any, state: Model) -> "DataSetsJson":
        return DataSetsJson(default=DEFAULT_DATA_SET,
                            datasets=[ds.name for ds in state.data_sets.values()])




class MetiersJson(BaseModel):
    metiers: list[MetierJson]

    @staticmethod
    def view_model(_: str, res: Tuple[DataSet, CompetencesMetiers], model: Model) -> "MetiersJson":
        (ds, __) = res
        return MetiersJson(metiers=[MetierJson.view_metier(None, None, m)
            for m in model.competences_metiers[ds].metiers()])


class CompetencesJson(BaseModel):
    competences: list[CompetenceJson]

    @staticmethod
    def view_model(_: str, res: Tuple[DataSet, CompetencesMetiers], model: Model) -> "CompetencesJson":
        (ds, __) = res
        return CompetencesJson(
                competences=[CompetenceJson.view_competence(None, None, c)
                    for c in model.competences_metiers[ds].competences()])
