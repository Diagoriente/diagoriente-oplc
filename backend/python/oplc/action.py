from typing import Callable, TypeVar, Any, Tuple

from oplc.model import Model, CompetencesMetiers, DataSet
from dataclasses import replace


I = TypeVar('I')
E = TypeVar('E')
Action = Callable[[I, E, Model], Model]

def update_data_set(_: str, t: Tuple[DataSet, CompetencesMetiers], state: Model) -> Model:
    (ds, cm) = t
    return replace(state,
            competences_metiers= state.competences_metiers | {ds: cm})

def identity_action(_: Any, __: Any, state: Model) -> Model:
    return state
