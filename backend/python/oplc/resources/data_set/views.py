from pydantic import BaseModel

from oplc.constants import DEFAULT_DATA_SET

from .model import DataSet

class DataSetJson(BaseModel):
    name: str

    @staticmethod
    def from_data_set(ds: DataSet) -> "DataSetJson":
        return DataSetJson(name=ds.name)


class DataSetsJson(BaseModel):
    default: str
    datasets: list[str]

    @staticmethod
    def from_data_sets(dss: list[DataSet]) -> "DataSetsJson":
        return DataSetsJson(default=DEFAULT_DATA_SET,
                            datasets=[ds.name for ds in dss])
