from oplc.model import Model, CompetencesMetiers, DataSet
from dataclasses import replace


def update_data_set(ds: DataSet, cm: CompetencesMetiers, state: Model) -> Model:
    return replace(state,
            competences_metiers= state.competences_metiers | {ds: cm})
