from typing import Callable

from oplc.model import Model, CompetencesMetiers, DataSet
from dataclasses import replace


Action = Callable[[Model], Model]

def update_data_set(ds: DataSet, cm: CompetencesMetiers) -> Action:
    def action(state: Model):
        return replace(state,
                competences_metiers= state.competences_metiers | {ds: cm})
    return action
