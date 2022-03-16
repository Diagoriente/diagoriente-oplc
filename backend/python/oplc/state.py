from oplc.model import Model, LocalCsv, GoogleDocsCsv

from pathlib import Path
from oplc.constants import LOCAL_DATASETS, GOOGLE_DOCS_DATASETS
from typing import Any


state = Model(
    competences_metiers={},
    data_sets=(
        {name: LocalCsv(name=name, path=Path(ds_spec["path"]))
            for name, ds_spec in LOCAL_DATASETS.items()}
        | {name: GoogleDocsCsv(name=name, key=ds_spec["key"], gid=ds_spec["gid"])
            for name, ds_spec in GOOGLE_DOCS_DATASETS.items()}
    )
)

class State:
    def __enter__(self) -> Model:
        global state
        self.state = state
        return self.state

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> bool:
        global state

        if (exc_type, exc_value, traceback) == (None, None, None):
            state = self.state
            return True
        else:
            # If an exception was raised, don't write the modified state back to
            # the global state.
            return False

