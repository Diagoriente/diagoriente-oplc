from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from oplc.constants import CORS_ALLOWED_ORIGINS, API_ROOT_PATH
from typing import Optional

from oplc.view import DataSetsJson, DataSetJson, MetiersJson, CompetencesJson
from oplc.effect import updated_data_set
from oplc.action import update_data_set
from oplc.state import State

# TODO: configure this
import logging
logging.getLogger().setLevel(logging.INFO)


app = FastAPI(root_path=API_ROOT_PATH)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/data_sets")
async def get_data_sets() -> Optional[DataSetsJson]:
    with State() as s:
        return DataSetsJson.view(s.data_sets)


@app.post("/metiers")
async def post_metiers(dataset: DataSetJson) -> Optional[MetiersJson]:
    with State() as s:
        ds = s.data_sets[dataset.name]
        cm = updated_data_set(ds, s)
        s = update_data_set(ds, cm, s)
        metiers = s.competences_metiers[ds].metiers()
        return MetiersJson.view(metiers)


@app.post("/competences")
async def post_competences(dataset: DataSetJson) -> Optional[CompetencesJson]:
    with State() as s:
        ds = dataset.decode(s)
        cm = updated_data_set(ds, s)
        s = update_data_set(ds, cm, s)
        competences = s.competences_metiers[ds].competences()
        return CompetencesJson.view(competences)
