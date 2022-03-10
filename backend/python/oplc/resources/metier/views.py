from pydantic import BaseModel

from oplc.resources.metier.model import Metier

class MetierJson(BaseModel, frozen=True):
    name: str

def metierJson(m: Metier) -> MetierJson:
    return MetierJson(name= m.name)
