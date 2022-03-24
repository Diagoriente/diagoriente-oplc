import json
import pandas as pa
import requests
from requests.exceptions import HTTPError
from datetime import datetime

from oplc.pipelines import (
        LocalCsv, GoogleDocsCsv, DataSource, DataPieceKind,
        local_csv_dir, local_csv_path, local_csv_path_meta,
        )
import logging



def pull_source(
        ds: DataSource,
        kind: DataPieceKind,
        skip_if_exists: bool=True
        ) -> LocalCsv:

    if not local_csv_dir(kind).exists() or skip_if_exists == False:
        logging.info(f'Pulling data source "{ds.name}"')

        if isinstance(ds, GoogleDocsCsv):
            res = requests.get(ds.url())
            res.encoding = "utf-8"

            try:
                res.raise_for_status()
            except HTTPError:
                raise HTTPError(f"Couldn't download Google docs spreadsheet with key {ds.key} and gid {ds.gid}")

            content = res.text

        else:
            with open(ds.path, "r") as f:
                content = f.read()

        local_csv_dir(kind).mkdir(parents=True, exist_ok=True)

        with open(local_csv_path(kind), "w") as f:
            f.write(content)

        with open(local_csv_path_meta(kind), "w") as f:
            f.write(json.dumps({
                    "kind": kind,
                    "date": datetime.utcnow().isoformat(),
                    "name": ds.name,
                  }))

    return load_local_csv(kind)


def load_local_csv(kind: DataPieceKind):
    with open(local_csv_path_meta(kind), "r") as f:
        meta = json.loads(f.read())
        return LocalCsv(
                kind=kind,
                date=datetime.fromisoformat(meta["date"]),
                name=meta["name"]
                )


def load_data_frame(ds: LocalCsv) -> pa.DataFrame :
    return pa.DataFrame(pa.read_csv(local_csv_path(ds.kind)))
