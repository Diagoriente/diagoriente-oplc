from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from oplc.constants import CORS_ALLOWED_ORIGINS, API_ROOT_PATH, DEFAULT_DATA_SET
from typing import Optional

from oplc.view import (
        DataSetsJson, DataSetJson, MetierJson, CompetenceJson,
        MetiersSuggestionJson, decode_competences_json, view_metiers_json,
        view_competences_json)
import oplc.effect as effect
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
async def post_metiers(
        dataset: Optional[DataSetJson] = None
        ) -> Optional[list[MetierJson]]:
    with State() as s:
        ds = dataset and dataset.decode(s) or s.data_sets[DEFAULT_DATA_SET]
        s = effect.load_data_set(ds, s)
        metiers = s.competences_metiers[ds].metiers()
        return view_metiers_json(metiers)


@app.post("/competences")
async def post_competences(
        dataset: Optional[DataSetJson] = None
        ) -> Optional[list[CompetenceJson]]:
    with State() as s:
        ds = dataset and dataset.decode(s) or s.data_sets[DEFAULT_DATA_SET]
        s = effect.load_data_set(ds, s)
        competences = s.competences_metiers[ds].competences()
        return view_competences_json(competences)


@app.post("/metiers_suggestion")
async def post_metiers_suggestion(
        competences: list[CompetenceJson],
        dataset: Optional[DataSetJson] = None,
        ) -> Optional[MetiersSuggestionJson]:
    with State() as s:
        ds = dataset and dataset.decode(s) or s.data_sets[DEFAULT_DATA_SET]
        s = effect.load_data_set(ds, s)
        cm = s.competences_metiers[ds]
        return MetiersSuggestionJson.view(
                cm.metiers_suggestion(decode_competences_json(competences)))
