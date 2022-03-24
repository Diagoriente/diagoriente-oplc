import logging
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from oplc.config import API_ROOT_PATH, CORS_ALLOWED_ORIGINS
from oplc.model import job_recommendation
from oplc.state import state
from oplc.view import (
        decode_experiences_json, JobRecommendationJson, view_jobs_json,
        view_skills_json, JobJson, SkillJson, ExperienceJson,
        view_experiences_json,
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
    with state() as s:
        experiences = s.dataset.experiences_skills.experiences()
        return view_experiences_json(experiences)


@app.get("/jobs")
async def get_jobs() -> Optional[list[JobJson]]:
    with state() as s:
        jobs = s.dataset.jobs_skills.jobs()
        return view_jobs_json(jobs)


@app.get("/skills")
async def get_skills() -> Optional[list[SkillJson]]:
    with state() as s:
        skills = s.dataset.experiences_skills.skills()
        return view_skills_json(skills)


@app.post("/jobs_recommendation")
async def post_jobs_recommendation(
        experiences: list[ExperienceJson],
        ) -> Optional[JobRecommendationJson]:
    with state() as s:
        jr = job_recommendation(
                s.dataset.experiences_skills,
                s.dataset.jobs_skills,
                decode_experiences_json(experiences)
                )
        return JobRecommendationJson.view(jr)
