from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from oplc.constants import CORS_ALLOWED_ORIGINS, API_ROOT_PATH

from oplc.resources.metier.views import MetierJson
from oplc.resources.competence.views import CompetenceJson
from oplc.resources.competences_metiers.controller import competences_metiers
from oplc.resources.data_set.views import DataSetJson, DataSetsJson
from oplc.resources.data_set.controller import data_set, data_sets

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
    return DataSetsJson.from_data_sets(data_sets())

@app.post("/metiers")
async def post_metiers(dataset: DataSetJson) -> list[MetierJson]:
    ds = data_set(dataset.name)
    return [MetierJson.from_metier(m) 
            for m in competences_metiers(ds).metiers()]

@app.post("/competences")
async def post_competences(dataset: DataSetJson) -> list[CompetenceJson]:
    ds = data_set(dataset.name)
    return [CompetenceJson.from_competence(m)
            for m in competences_metiers(ds).competences()]
