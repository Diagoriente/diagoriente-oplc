from pydantic import BaseModel, Field
from typing import Annotated, Union, Literal
from oplc.resources.data_set.model import DataSet, LocalCsv, GoogleDocsCsv
from pathlib import Path

class LocalCsvJson(BaseModel):
    kind: Literal['local_csv']
    path: Path

    def to_data_set(self) -> DataSet:
        return LocalCsv(path=self.path)

class GoogleDocsCsvJson(BaseModel):
    kind: Literal['google_docs_csv']
    key: str
    gid: str

    def to_data_set(self) -> DataSet:
        return GoogleDocsCsv(key=self.key, gid=self.gid)

DataSetJson = Annotated[Union[LocalCsvJson, GoogleDocsCsvJson], Field(..., discriminator='kind') ]

