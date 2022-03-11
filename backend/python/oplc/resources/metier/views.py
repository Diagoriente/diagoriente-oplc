from pydantic import BaseModel

from oplc.resources.metier.model import Metier

class MetierJson(BaseModel, frozen=True):
    name: str

    @staticmethod
    def from_metier(m: Metier) -> "MetierJson":
        return MetierJson.construct(name= m.name)
