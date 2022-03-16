from oplc.action import Action
from oplc.model import Model, LocalCsv, GoogleDocsCsv

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

def get_state():
    return state

def run_action(action: Action) -> Model:
    global state
    state = action(state)
    return state

