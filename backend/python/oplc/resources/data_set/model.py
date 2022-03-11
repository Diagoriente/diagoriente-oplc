from dataclasses import dataclass
from pathlib import Path
from typing import Union
from oplc.constants import DATASET_CACHE_DIR


@dataclass(frozen=True)
class LocalCsv:
    path: Path

@dataclass(frozen=True)
class GoogleDocsCsv:
    key: str
    gid: str

    def url(self) -> str:
        return f"https://docs.google.com/spreadsheets/d/{self.key}/export?gid={self.gid}&format=csv"

    def cache_path(self) -> Path:
        return DATASET_CACHE_DIR / Path(f"google_sheet_{self.key}_{self.gid}.csv")

DataSet = Union[LocalCsv, GoogleDocsCsv]
