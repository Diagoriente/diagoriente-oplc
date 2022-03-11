from pydantic import BaseModel

from oplc.resources.competence.model import Competence

class CompetenceJson(BaseModel, frozen=True):
    name: str

    @staticmethod
    def from_competence(m: Competence) -> "CompetenceJson":
        return CompetenceJson(name=m.name)

