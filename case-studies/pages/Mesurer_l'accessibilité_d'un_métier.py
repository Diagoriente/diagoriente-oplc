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

st.write("""
        Entrez vos expériences professionnelles ci-dessous pour connaître
        d'autres métiers qui correspondent à vos compétences.
""")

data = etl.get_data()

skills = model.mk_skills(data.skills)
jobs = model.mk_jobs(data.jobs)
sectors = model.mk_sectors(data.sectors)
jobs_skills = model.mk_jobs_skills(data.jobs_skills)
skill_cooc = model.skill_cooccurrence(jobs_skills)

default_indiv_exp = [
        (124, datetime.fromisoformat("2018-06-01"), datetime.fromisoformat("2020-12-31")),
        (125, datetime.fromisoformat("2020-01-01"), datetime.fromisoformat("2021-12-31")),
        (126, datetime.fromisoformat("2022-01-01"), datetime.fromisoformat("2022-05-31")),
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
                jobs.index,
                key=i,
                index=jobs.index.tolist().index(def_job_id),
                format_func=lambda x: f"{x}: ({jobs.loc[x, 'ROME']}) {jobs.loc[x, 'title']}",
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
            .assign(Nom=[jobs.loc[i, "title"] for i in experience_weights.job_id])
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
            .assign(Nom=[skills.loc[i, "title"] for i in indiv_skills_nonzero.index])
            .rename(columns={"weight": "Importance"})
            .loc[:, ["Nom", "Importance"]]
    )


st.header("Métiers du plus accessible au moins accessible")

with st.expander("Que signifie l'accessibilité d'un métier ?"):
    st.write("""
        L'accessibilité d'un métier est égale à 1 quand vous avez développé les compétences qu'il nécessite de manière égale et que vous n'avez développé aucune autre compétence. Ceci nous permet de vous proposer d'abord des métiers qui vous permettront d'exercer le plus grand nombre possible de vos compétences et seulement ensuite les métiers qui n'exploiteront qu'une partie de vos compétences.

        Au contraire, l'accessibilité vaut 0 lorsque vous n'avez aucune compétence en commun avec celles demandées pour le métier.
        """)

with st.expander("Que signifie l'accessibilité d'une compétence ?"):
    st.write("""
        L'accessibilité d'une compétence traduit la facilité avec laquelle vous devriez pouvoir l'acquérir. Elle vaut 0 pour les compétences difficiles et 1 pour les compétences faciles.

        Elle dépend des compétences qui sont exercées conjointement avec la compétence considérée. Par exemple, la compétence "Observer, visualiser, s'orienter" est exercée conjointement à "Aménager, entretenir un espace naturel" dans 4 métiers: Sylviculteur / Sylvicultrice, Aménagement et entretien des espaces verts, Bûcheronnage et élagage et Entretien des espaces naturels. Nous faisons l'hypothèse que si vous matriser l'une, l'autre devrait être plus facile à acquérir.
            """)

indiv_main_sector = jobs.loc[
        experience_weights.loc[lambda x: x.weight.idxmax(), "job_id"],
        "sector"
        ]

most_accessible_jobs = dist_job.sort_values(ascending=False)


hide_practiced_jobs = st.checkbox("Cacher les métiers déjà exercés", value = True)

if hide_practiced_jobs:
    most_accessible_jobs = most_accessible_jobs.drop(indiv_exp.job_id)


indiv_sector = st.selectbox(f"Votre secteur d'activité principal est :",
                sectors.index,
                key="indiv_sector",
                index=sectors.index.tolist().index(indiv_main_sector),
                format_func=lambda x: f"{x}: ({sectors.loc[x, 'ROME']}) {sectors.loc[x, 'title']}",
                )

same_sector_first = st.checkbox("Montrer d'abord les métiers du même secteur d'activité", value = True)

if same_sector_first:
    select_same_sector = jobs.sector == indiv_sector
    same_sector_jobs = most_accessible_jobs.loc[select_same_sector].sort_values(ascending=False)
    other_sectors_jobs = most_accessible_jobs.loc[~select_same_sector].sort_values(ascending=False)
    most_accessible_jobs = pa.concat([same_sector_jobs, other_sectors_jobs])


n_recommended_jobs = st.number_input("Combien de métiers afficher ?", 1, 30, value=10, step=5)

most_accessible_jobs = most_accessible_jobs.head(n_recommended_jobs)

job_list_markdown = ""

for j in most_accessible_jobs.index:

    job_list_markdown += f"1. **{jobs.loc[j, 'title']}** (accessibilité du métier: {dist_job.loc[j]:.2f})\n"

    job_list_markdown += f"    - En raison de votre expérience pour :\n"
    for s in skill_contrib.loc[j, :].sort_values(ascending=False).loc[lambda x: x > 0].index:
        job_list_markdown += f"       - *{skills.loc[s, 'title']}*\n"

    job_list_markdown += f"    - Vous devrez développer les compétences suivantes :\n"
    for s in skill_gap.loc[j, :].sort_values(ascending=False).loc[lambda x: x >= 1.0].index:
        sa, scontrib = model.skill_accessibility(skill_cooc, indiv_skills)
        job_list_markdown += f"       - *{skills.loc[s, 'title']}* (accessibilité de la compténce: {sa.loc[s]:.2f} car vous savez déjà "
        for sc in scontrib.loc[s,:].sort_values(ascending=False).loc[lambda x: x > 0].index:
            job_list_markdown += f"*{skills.loc[sc, 'title']}*; "
        job_list_markdown += ")\n"
st.write(job_list_markdown)
