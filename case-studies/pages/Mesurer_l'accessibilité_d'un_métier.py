import networkx as nx
import oplc_etl.pipelines.neo4j as etl
from oplc_model import model_skill_cooc as model
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

_jobs, _skills, _jobs_skills = etl.get_data()

skills = model.mk_skills(_skills)
jobs = model.mk_jobs(_jobs)
jobs_skills = model.mk_jobs_skills(_jobs_skills)
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

with st.form(key="Vos expériences"):
    indiv_exp = pa.DataFrame({
        "job_id": np.empty(int(indiv_exp_count), dtype=int),
        "begin": np.empty(int(indiv_exp_count), dtype=datetime),
        "end": np.empty(int(indiv_exp_count), dtype=datetime),
        "duration": np.empty(int(indiv_exp_count), dtype=float),
        "recency": np.empty(int(indiv_exp_count), dtype=float),
        "weight": np.empty(int(indiv_exp_count), dtype=float),
        })


    for i in range(int(indiv_exp_count)):

        if i < len(default_indiv_exp):
            (def_job_id, def_begin, def_end) = default_indiv_exp[i]
        else:
            def_job_id = 0
            def_begin = None
            def_end = None

        st.subheader(f"Expérience {i+1}")
        indiv_exp.loc[i, "job_id"] = st.selectbox(f"Intitulé",
                jobs.keys(),
                key=i,
                index=def_job_id,
                format_func=lambda x: f"{x}: {jobs[x].name}",
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

    st.form_submit_button("Obtenir des recommandations")


indiv_exp, indiv_skills = model.experience_weights(indiv_exp, jobs_skills)

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
