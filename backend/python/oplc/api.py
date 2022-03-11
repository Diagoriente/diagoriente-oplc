from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from oplc.constants import CORS_ALLOWED_ORIGINS, API_ROOT_PATH

from oplc.resources.metier.views import MetierJson
from oplc.resources.competence.views import CompetenceJson
from oplc.resources.competences_metiers.controller import competences_metiers
from oplc.resources.data_set.views import DataSetJson

app = FastAPI(root_path=API_ROOT_PATH)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/metiers")
async def metiers(dataset: DataSetJson) -> list[MetierJson]:
    return [MetierJson.from_metier(m) 
            for m in competences_metiers(dataset.to_data_set()).metiers()]

@app.post("/competences")
async def competences(dataset: DataSetJson) -> list[CompetenceJson]:
    return [CompetenceJson.from_competence(m)
            for m in competences_metiers(dataset.to_data_set()).competences()]
