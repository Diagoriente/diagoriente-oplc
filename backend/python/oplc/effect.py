import pandas as pa
import requests
from requests.exceptions import HTTPError
from typing import Callable, TypeVar, Any, Tuple

from oplc.model import Model, CompetencesMetiers, DataSet, GoogleDocsCsv
import logging


def pull_source(ds: DataSet) -> None:
    if isinstance(ds, GoogleDocsCsv):
        logging.info(f"Pulling source of data set {ds.name}")
        res = requests.get(ds.url())
        res.encoding = "utf-8"

        try:
            res.raise_for_status()
        except HTTPError:
            raise HTTPError(f"Couldn't download Google docs spreadsheet with key {ds.key} and gid {ds.gid}")

        ds.cache_path().parent.mkdir(parents=True, exist_ok=True)
        with open(ds.cache_path(), "w") as f:
            f.write(res.text)
    else:
        pass


def data_frame(ds: DataSet) -> pa.DataFrame :
    if isinstance(ds, GoogleDocsCsv):
        return pa.read_csv(ds.cache_path(), index_col=0)
    else:
        return pa.read_csv(ds.path, index_col=0)


def is_cached(ds: DataSet) -> bool:
    if isinstance(ds, GoogleDocsCsv):
        return ds.cache_path().is_file()
    else:
        return True


M = TypeVar('M')
E = TypeVar('E')
Effect = Callable[[Model, M], E]


def updated_data_set(force_update: bool = False) -> Effect[str, Tuple[DataSet, CompetencesMetiers]]:
    def effect(state: Model, data_set_name: str)-> Tuple[DataSet, CompetencesMetiers]:
        ds = state.data_sets[data_set_name]

        do_pull = not is_cached(ds) or force_update

        if do_pull:
            logging.info(f"Data set pull from source requested for {ds.name} .")
            pull_source(ds)

        if do_pull or ds not in state.competences_metiers:
            logging.info(f"Data set update requested for {ds.name} .")
            df = data_frame(ds)
            cm = CompetencesMetiers(df=df) # type:ignore
            return ds, cm
        else:
            return ds, state.competences_metiers[ds]


    return effect


def empty_effect(_: Model, __: Any) -> None:
    return None



