from oplc.action import Action
from oplc.view import View
from oplc.model import Model, LocalCsv, GoogleDocsCsv
from oplc.effect import Effect
from typing import TypeVar

from pathlib import Path
from oplc.constants import LOCAL_DATASETS, GOOGLE_DOCS_DATASETS


state = Model(
    competences_metiers={},
    data_sets=(
        {name: LocalCsv(name=name, path=Path(ds_spec["path"]))
            for name, ds_spec in LOCAL_DATASETS.items()}
        | {name: GoogleDocsCsv(name=name, key=ds_spec["key"], gid=ds_spec["gid"])
            for name, ds_spec in GOOGLE_DOCS_DATASETS.items()}
    )
)

I = TypeVar('I')
E = TypeVar('E')
V = TypeVar('V')
def update(msg: I, effect: Effect[I, E], action: Action[I, E], view: View[I, E, Model, V]) -> V:
    global state
    res = effect(state, msg)
    state = action(msg, res, state)
    return view(msg, res, state)

