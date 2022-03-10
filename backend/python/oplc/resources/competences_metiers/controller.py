from oplc.resources.competences_metiers.model import CompetencesMetiers
from oplc.resources.data_set.model import DataSet
from oplc.resources.data_set.controller import data_frame
from oplc.resources.metier.model import Metier
from oplc.resources.competence.model import Competence


def competences_metiers(ds: DataSet) -> CompetencesMetiers:
    return CompetencesMetiers(df=data_frame(ds)) # type:ignore


def metiers(ds: DataSet) -> list[Metier]:
    return competences_metiers(ds).metiers()


def competences(ds: DataSet) -> list[Competence]:
    return competences_metiers(ds).competences()


