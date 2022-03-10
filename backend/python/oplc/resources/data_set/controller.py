from functools import lru_cache

import pandas as pa
import requests
from requests.exceptions import HTTPError

from oplc.resources.data_set.model import *

@lru_cache(maxsize=10)
def data_frame(ds: DataSet, update: bool=False) -> pa.DataFrame :
    if isinstance(ds, GoogleDocsCsv):
        pull_source(ds, update)
        return pa.read_csv(ds.cache_path(), index_col=0)
    else:
        return pa.read_csv(ds.path, index_col=0)


def pull_source(ds: DataSet, update: bool=False) -> None:
    if is_cached(ds) and not update:
        return

    if isinstance(ds, GoogleDocsCsv):
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


def is_cached(ds: DataSet) -> bool:
    if isinstance(ds, GoogleDocsCsv):
        return ds.cache_path().is_file()
    else:
        return True