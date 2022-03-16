import pandas as pa
import requests
from requests.exceptions import HTTPError
from dataclasses import replace

from oplc.model import CompetencesMetiers, DataSet, GoogleDocsCsv, Model
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
        return pa.DataFrame(pa.read_csv(ds.cache_path(), index_col=0))
    else:
        return pa.DataFrame(pa.read_csv(ds.path, index_col=0))


def is_cached(ds: DataSet) -> bool:
    if isinstance(ds, GoogleDocsCsv):
        return ds.cache_path().is_file()
    else:
        return True


def load_data_set(ds: DataSet, state: Model, always_update: bool = False) -> Model:
    do_pull = not is_cached(ds) or always_update

    if do_pull:
        logging.info(f"Data set pull from source requested for {ds.name} .")
        pull_source(ds)

    if do_pull or ds not in state.competences_metiers:
        logging.info(f"Data set update requested for {ds.name} .")
        df = data_frame(ds)
        cm = CompetencesMetiers(df=df) # type:ignore
        return replace(state,
            competences_metiers= state.competences_metiers | {ds: cm})
    else:
        return state



