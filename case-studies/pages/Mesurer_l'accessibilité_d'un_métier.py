import networkx as nx
from oplc_etl import pipelines as etl
from oplc_model import model
import numpy as np
import pandas as pa
import streamlit as st
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource
from typing import Callable
from datetime import datetime
import logging

logging.getLogger().setLevel(logging.INFO)

st.header("Mesurer l'accessibilité d'un métier")

# skills = oplc.model.model.skills
# 
# skills_jobs = oplc.model.model.jobs_skills.df.transpose()
# # Remove skills that are not associated to any job
# skills_jobs = skills_jobs.loc[skills_jobs.sum(axis=1) > 0, :]
# 
# skill_cooc = skills_jobs.dot(skills_jobs.transpose())
# 
# jobs_skills = skills_jobs.transpose()
# 
# jobs = (pa.DataFrame([(x.id, x.name) for x in oplc.model.model.jobs.values()],
#                      columns=["id", "name"],
#                     )
#         .set_index("id")
#        )
# 
# experiences = (pa.DataFrame([(x.id, x.name, x.exp_type) 
#                              for x in oplc.model.model.experiences.values()],
#                             columns=["id", "name", "type"],
#                             )
#               .set_index("id")
#               )
# experiences_skills = oplc.model.model.experiences_skills.df

skills = model.mk_skills(etl.skills())
jobs = model.mk_jobs(etl.jobs())
experiences = model.mk_experiences(etl.experiences())
jobs_skills = model.mk_jobs_skills(etl.jobs_skills())
experiences_skills = model.mk_experiences_skills(etl.experiences_skills())
skill_cooc = model.skill_cooccurrence(jobs_skills)

default_indiv_exp = [
        (1, datetime.fromisoformat("2018-06-01"), datetime.fromisoformat("2020-12-31")),
        (2, datetime.fromisoformat("2020-01-01"), datetime.fromisoformat("2021-12-31")),
        (3, datetime.fromisoformat("2022-01-01"), datetime.fromisoformat("2022-05-31")),
        ]

indiv_exp_count = st.number_input(
        "Combien d'expériences voulez-vous renseigner ?",
        min_value=0,
        max_value=None,
        value=len(default_indiv_exp))

indiv_exp = pa.DataFrame({
    "experience_id": np.empty(int(indiv_exp_count), dtype=int),
    "begin": np.empty(int(indiv_exp_count), dtype=datetime),
    "end": np.empty(int(indiv_exp_count), dtype=datetime),
    "duration": np.empty(int(indiv_exp_count), dtype=float),
    "recency": np.empty(int(indiv_exp_count), dtype=float),
    "weight": np.empty(int(indiv_exp_count), dtype=float),
    "job_id": np.empty(int(indiv_exp_count), dtype=int),
    })



for i in range(int(indiv_exp_count)):

    if i < len(default_indiv_exp):
        (def_exp_id, def_begin, def_end) = default_indiv_exp[i]
    else:
        def_exp_id = 0
        def_begin = None
        def_end = None

    st.subheader(f"Expérience {i+1}")
    indiv_exp.loc[i, "experience_id"] = st.selectbox(f"Intitulé",
            experiences.keys(),
            key=i,
            index=def_exp_id,
            format_func=lambda x: f"{x}: ({experiences[x].exp_type}) {experiences[x].name}",
            )
    (col1, col2) = st.columns(2)

    with col1:
        indiv_exp.loc[i, "begin"] = st.date_input(
                "Date de début",
                key=i,
                value=def_begin
                )

    with col2:
        indiv_exp.loc[i, "end"] = st.date_input(
                "Date de fin",
                key=i,
                value=def_end
                )


# today = datetime.today()
# 
# for i in indiv_exp.index:
#     begin = pa.to_datetime(indiv_exp.loc[i, "begin"])
#     end = pa.to_datetime(indiv_exp.loc[i, "end"])
#     years = list(range(begin.year, end.year + 1))
#     start_day_per_year = (
#             [begin]
#             + [datetime(year=y, month=1, day=1) for y in years[1:]]
#             )
#     end_day_per_year = (
#             [datetime(year=y, month=12, day=31) for y in years[:-1]]
#             + [end]
#             )
#     days_per_year = [(datetime(year=y+1, month=1, day=1) - datetime(year=y, month=1, day=1)).days 
#                       for y in years]
#     # Proportion of year worked for each year
#     year_proportion = [((e - s).days + 1) / d
#                        for s,e,d
#                        in zip(start_day_per_year, end_day_per_year, days_per_year)]
#     # Experience recency per year
#     year_recency = [(today - e).days / d for d, e in zip(days_per_year, end_day_per_year)]
# 
#     year_weight = [p / (r + 1) for p, r in zip(year_proportion, year_recency)]
# 
#     experience_weight = sum(year_weight)
# 
#     indiv_exp.loc[i, "duration"] = sum(year_proportion)
#     indiv_exp.loc[i, "rencency"] = year_recency[-1]
#     indiv_exp.loc[i, "weight"] = experience_weight
#     indiv_exp.loc[i, "job_id"] = jobs.index[jobs.name == experiences.loc[indiv_exp.loc[i, "experience_id"], "name"]][0]
# 

indiv_exp, indiv_skills = model.experience_weights(indiv_exp, jobs, experiences,
                                                   experiences_skills)

st.header("Vous avez les compétences suivantes, de la plus importante à la moins importante")

indiv_skills_nonzero = (indiv_skills.loc[indiv_skills.weight > 0, :]
                       .sort_values(by="weight", ascending=False)
                       )

st.table(pa.DataFrame({
     "Nom": [skills[i].name for i in indiv_skills_nonzero.index],
     "Importance de la compétence": indiv_skills_nonzero.weight,
     }))


st.header("Métiers du plus accessible au moins accessible")


metric = st.selectbox("Mesure de distance:", ["correlation", "cosine"], index=1)

# dist_job = pa.Series(np.empty(jobs_skills.shape[0]),
#                       index=jobs_skills.index,
#                      )
# 
# for j in jobs_skills.index:
#     dist_job.loc[j] = pdist([indiv_skills.loc[jobs_skills.columns].weight,
#                              jobs_skills.loc[j, :],
#                              ],
#                              metric=metric)
# 
# dist_job_sorted = dist_job.sort_values()

dist_job = model.job_distance(jobs_skills, indiv_skills, metric)

job_access = (pa.DataFrame({
                "Nom": [jobs[i].name for i in dist_job.index],
                "Accessibilité": dist_job,
                "Années d'expérience": [indiv_exp.loc[lambda x: x.job_id == i, "duration"].sum() for i in dist_job.index],
             }))

hide_practiced_jobs = st.checkbox("Cacher les métiers déjà exercés", value = True)

if hide_practiced_jobs:
    job_access = job_access.loc[
            lambda x: x.loc[:, "Années d'expérience"] == 0
            ]
st.table(job_access.head(30))
