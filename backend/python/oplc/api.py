import logging
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from oplc.config import API_ROOT_PATH, CORS_ALLOWED_ORIGINS
from oplc.model import model
from oplc.view import (
        decode_experiences_json, JobRecommendationJson, view_jobs_json,
        view_skills_json, JobJson, SkillJson, ExperienceJson,
        view_experiences_json, view_job_recommendation_json
        )

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
async def get_experiences() -> Optional[list[ExperienceJson]]:
    return view_experiences_json(model)


@app.get("/jobs")
async def get_jobs() -> Optional[list[JobJson]]:
    return view_jobs_json(model)


@app.get("/skills")
async def get_skills() -> Optional[list[SkillJson]]:
    return view_skills_json(model)


@app.post("/jobs_recommendation")
async def post_jobs_recommendation(
        experiences: list[ExperienceJson],
        ) -> Optional[JobRecommendationJson]:
    return view_job_recommendation_json(
            model, 
            decode_experiences_json(experiences))
