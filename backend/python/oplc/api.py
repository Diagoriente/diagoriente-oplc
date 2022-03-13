from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from oplc.constants import CORS_ALLOWED_ORIGINS, API_ROOT_PATH

from oplc.view import DataSetsJson, DataSetJson, MetiersJson, CompetencesJson
from oplc.effect import updated_data_set, empty_effect
from oplc.action import update_data_set, identity_action
from oplc.loop import update

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
    return update(
            msg=None,
            effect=empty_effect,
            action=identity_action,
            view=DataSetsJson.view_model)


@app.post("/metiers")
async def post_metiers(dataset: DataSetJson) -> MetiersJson:
    global state
    return update(
            msg=dataset.name,
            effect=updated_data_set(),
            action=update_data_set,
            view=MetiersJson.view_model)


@app.post("/competences")
async def post_competences(dataset: DataSetJson) -> CompetencesJson:
    # Interpret input
    return update(
            msg=dataset.name,
            effect=updated_data_set(),
            action=update_data_set,
            view=CompetencesJson.view_model)

