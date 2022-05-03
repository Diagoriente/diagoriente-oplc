"""HTTP API.

The functions define endpoints. They put together the pieces from oplc.model,
oplc.view and oplc.actions in the lines of
https://www.infoq.com/articles/no-more-mvc-frameworks/.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from oplc.config import API_ROOT_PATH, CORS_ALLOWED_ORIGINS
from oplc import model, action, view
import networkx as nx

logging.getLogger().setLevel(logging.INFO)


app = FastAPI(root_path=API_ROOT_PATH)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/experiences")
async def get_experiences() -> dict[view.ExperienceIdJson, view.ExperienceJson]:
    return view.experiences_json(model.get())


@app.get("/jobs")
async def get_jobs() -> dict[view.ExperienceIdJson, view.JobJson]:
    return view.jobs_json(model.get())


@app.get("/skills")
async def get_skills() -> dict[view.SkillIdJson, view.SkillJson]:
    return view.skills_json(model.get())


@app.post("/pull_data_source")
async def post_pull_data_source() -> None:
    model.present(action.pull_data_source())


@app.post("/job_recommendation")
async def post_job_recommendation(
        experiences: list[view.ExperienceIdJson],
        return_graph: bool = False,
        ) -> view.JobRecommendationJson:
    return view.job_recommendation_json(
            model.get(),
            experiences,
            return_graph,
            lambda g: nx.betweenness_centrality(g, endpoints=True),
            )
