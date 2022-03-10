from pydantic import BaseModel
import pandas as pa
from typing import Iterable
from oplc.resources.metier.model import Metier
from oplc.resources.competence.model import Competence

class CompetencesMetiers(BaseModel, frozen=True, arbitrary_types_allowed=True):
    df: pa.DataFrame

    def metiers(self) -> list[Metier]:
        ms: Iterable[str] = self.df.index
        return [Metier(name=m) for m in ms]

    def competences(self) -> list[Competence]:
        cs: Iterable[str] = self.df.columns
        return [Competence(name=c) for c in cs]
