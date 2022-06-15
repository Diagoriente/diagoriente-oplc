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
    job_id = np.empty(int(indiv_exp_count), dtype=int)
    begin = np.empty(int(indiv_exp_count), dtype=datetime)
    end = np.empty(int(indiv_exp_count), dtype=datetime)


    for i in range(int(indiv_exp_count)):

        if i < len(default_indiv_exp):
            (def_job_id, def_begin, def_end) = default_indiv_exp[i]
        else:
            def_job_id = 0
            def_begin = None
            def_end = None

        st.subheader(f"Expérience {i+1}")
        job_id[i] = st.selectbox(f"Intitulé",
                jobs.keys(),
                key=i,
                index=def_job_id,
                format_func=lambda x: f"{x}: {jobs[x].name}",
                )
        (col1, col2) = st.columns(2)

        with col1:
            begin[i] = st.date_input(
                    "Date de début",
                    key=i,
                    value=def_begin
                    )

        with col2:
            end[i] = st.date_input(
                    "Date de fin",
                    key=i,
                    value=def_end
                    )

    st.form_submit_button("Obtenir des recommandations")

indiv_exp = model.mk_individual_experiences(job_id, begin, end)

experience_weights, indiv_skills, dist_job, skill_contrib, skill_gap = (
        model.job_accessibility_from_experiences(
            indiv_exp,
            jobs_skills,
        )
)


indiv_skills_nonzero = (indiv_skills.loc[indiv_skills.weight > 0, :]
                       .sort_values(by="weight", ascending=False)
                       )


with st.expander("Expériences (détails)"):
    st.table(
            experience_weights
            .assign(Nom=[jobs[i].name for i in experience_weights.job_id])
            .rename(columns={
                "begin": "Début",
                "end": "Fin",
                "duration": "Durée (années)",
                "recency": "Récence (années)",
                "weight": "Importance",
                })
            .loc[:, ["Nom", "Début", "Fin", "Durée (années)", "Récence (années)", "Importance"]]
    )


with st.expander("Compétences (détails)"):
    st.table(
            indiv_skills_nonzero
            .assign(Nom=[skills[i].name for i in indiv_skills_nonzero.index])
            .rename(columns={"weight": "Importance"})
            .loc[:, ["Nom", "Importance"]]
    )


st.header("Métiers du plus accessible au moins accessible")

st.info("""
Pour qu'un métier ait une correspondance de 1, il faut que la personne ait développé toutes les compétences demandées par le métier de manière égale. Si elle a aussi développé d'autres compétences ou si elle a développé ses compétences de manière inégale, la correspondante diminue.
""")

n_recommended_jobs = st.slider("Combien de métiers afficher ?", 1, len(dist_job), value=20)

most_accessible_jobs = dist_job.head(n_recommended_jobs).index

hide_practiced_jobs = st.checkbox("Cacher les métiers déjà exercés", value = True)

if hide_practiced_jobs:
    most_accessible_jobs = most_accessible_jobs.drop(indiv_exp.job_id)

job_list_markdown = ""

for j in most_accessible_jobs:

    job_list_markdown += f"- **{jobs[j].name}** (correspondance: {dist_job.loc[j]:.2f})\n"

    job_list_markdown += f"    - En raison de votre expériences pour :\n"
    for s in skill_contrib.loc[j, :].sort_values(ascending=False).loc[lambda x: x > 0].index:
        job_list_markdown += f"       - {skills[s].name} (contribution: {skill_contrib.loc[j, s] * 100:.0f}%)\n"

    job_list_markdown += f"    - Vous devrez d'avantage développer les compétences suivantes :\n"
    for s in skill_gap.loc[j, :].sort_values(ascending=False).loc[lambda x: x > 0].index:
        job_list_markdown += f"       - {skills[s].name} (gap: {skill_gap.loc[j, s] * 100:.0f}%)\n"
st.write(job_list_markdown)
