from pydantic import BaseModel

from oplc.constants import DEFAULT_DATA_SET
from oplc.model import DataSet, Metier, Competence, Model, MetiersSuggestion

from typing import Callable, TypeVar

T = TypeVar('T')
U = TypeVar('U')
View = Callable[[T], U]


class MetierJson(BaseModel, frozen=True):
    name: str

    @staticmethod
    def view(m: Metier) -> "MetierJson":
        return MetierJson(name=m.name)


class CompetenceJson(BaseModel, frozen=True):
    name: str

    @staticmethod
    def view(m: Competence) -> "CompetenceJson":
        return CompetenceJson(name=m.name)

    def decode(self) -> Competence:
        return Competence(name=self.name)



class DataSetJson(BaseModel):
    name: str

    @staticmethod
    def view(ds: DataSet) -> "DataSetJson":
        return DataSetJson(name=ds.name)

    def decode(self, model: Model) -> DataSet:
        try:
            return model.data_sets[self.name]
        except KeyError:
            raise KeyError(f"Data set {self.name} not found in current model state.")


class DataSetsJson(BaseModel):
    default: str
    datasets: list[str]

    @staticmethod
    def view(dss: dict[str, DataSet]) -> "DataSetsJson":
        return DataSetsJson(default=DEFAULT_DATA_SET,
                            datasets=[ds.name for ds in dss.values()])



def view_metiers_json(metiers: list[Metier]) -> list[MetierJson]:
    return [MetierJson.view(m) for m in metiers]


def view_competences_json(competences: list[Competence]) -> list[CompetenceJson]:
    return [CompetenceJson.view(c) for c in competences]


def decode_competences_json(competences: list[CompetenceJson]) -> list[Competence]:
    return [c.decode() for c in competences]


class MetierWithScoreJson(BaseModel):
    metier: MetierJson
    score: float


class MetiersSuggestionJson(BaseModel):
    scores: list[MetierWithScoreJson]

    @staticmethod
    def view(metiers_suggestion: MetiersSuggestion) -> "MetiersSuggestionJson":
        scores = [
            MetierWithScoreJson(metier=MetierJson.view(m), score=s)
            for m, s in metiers_suggestion.items()]
        return MetiersSuggestionJson(scores=scores)
