from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from oplc.constants import CORS_ALLOWED_ORIGINS, API_ROOT_PATH

from oplc.resources.metier.views import MetierJson, metierJson
from oplc.resources.competence.views import CompetenceJson, competenceJson
from oplc.resources.competences_metiers.controller import competences_metiers
from oplc.resources.data_set.model import DataSet

app = FastAPI(root_path=API_ROOT_PATH)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/metiers")
async def metiers(dataset: DataSet) -> list[MetierJson]:
    return [metierJson(m) for m in competences_metiers(dataset).metiers()]

@app.post("/competences")
async def competences(dataset: DataSet) -> list[CompetenceJson]:
    return [competenceJson(m) for m in competences_metiers(dataset).competences()]
