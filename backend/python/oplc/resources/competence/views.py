from pydantic import BaseModel

from oplc.resources.competence.model import Competence

class CompetenceJson(BaseModel, frozen=True):
    name: str

def competenceJson(m: Competence) -> CompetenceJson:
    return CompetenceJson(name= m.name)

