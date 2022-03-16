from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from oplc.constants import CORS_ALLOWED_ORIGINS, API_ROOT_PATH

from oplc.view import DataSetsJson, DataSetJson, MetiersJson, CompetencesJson
from oplc.effect import updated_data_set
from oplc.action import update_data_set
from oplc.state import get_state, run_action

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
async def get_data_sets() -> DataSetsJson:
    return DataSetsJson.view(get_state().data_sets)


@app.post("/metiers")
async def post_metiers(dataset: DataSetJson) -> MetiersJson:
    state = get_state()
    ds = state.data_sets[dataset.name]
    cm = updated_data_set(ds)
    run_action(update_data_set(ds, cm))
    return MetiersJson.view(get_state().competences_metiers[ds].metiers())


@app.post("/competences")
async def post_competences(dataset: DataSetJson) -> CompetencesJson:
    state = get_state()
    ds = state.data_sets[dataset.name]
    cm = updated_data_set(ds)
    run_action(update_data_set(ds, cm))
    return CompetencesJson.view(get_state().competences_metiers[ds].competences())


