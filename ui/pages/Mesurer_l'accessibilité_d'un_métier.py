from pathlib import Path
from os import fdopen
import networkx as nx
import oplc_etl.pipelines.neo4j as etl
from oplc_model import model_skill_cooc as m
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


@st.cache(max_entries=1)
def get_data():
    data = etl.get_data()

    skills = m.mk_skills(data.skills)
    jobs = m.mk_jobs(data.jobs)
    sectors = m.mk_sectors(data.sectors)
    jobs_skills = m.mk_jobs_skills(data.jobs_skills)
    skill_cooc = m.skill_cooccurrence(jobs_skills)

    return (skills, jobs, sectors, jobs_skills, skill_cooc)

skills, jobs, sectors, jobs_skills, skill_cooc = get_data()



default_indiv_exp = [
        (124, datetime.fromisoformat("2018-06-01"), datetime.fromisoformat("2020-12-31")),
        (125, datetime.fromisoformat("2020-01-01"), datetime.fromisoformat("2021-12-31")),
        (126, datetime.fromisoformat("2022-01-01"), datetime.fromisoformat("2022-05-31")),
        ]

if 'exp_input_job_id' not in st.session_state:
    st.session_state.exp_input_job_id = [124,125,126]
    st.session_state.exp_input_begin = [datetime.fromisoformat("2018-06-01"),
                                        datetime.fromisoformat("2020-01-01"),
                                        datetime.fromisoformat("2022-01-01"),
                                        ]
    st.session_state.exp_input_end = [datetime.fromisoformat("2020-12-31"),
                                      datetime.fromisoformat("2021-12-31"),
                                      datetime.fromisoformat("2022-05-31"),
                                      ]


def add_exp_input():
    st.session_state.exp_input_job_id.append(124)
    st.session_state.exp_input_begin.append(datetime.fromisoformat("2018-06-01"))
    st.session_state.exp_input_end.append(datetime.fromisoformat("2020-12-31"))


def rm_exp_input(i: int):
    st.session_state.exp_input_job_id.pop(i)
    st.session_state.exp_input_begin.pop(i)
    st.session_state.exp_input_end.pop(i)


st.header("Quelles sont vos expériences professionnelles ?")

for i in range(len(st.session_state.exp_input_job_id)):

    st.subheader(f"Expérience {i+1}")
    st.session_state.exp_input_job_id[i] = st.selectbox(f"Intitulé",
            jobs.index,
            index=jobs.index.tolist().index(st.session_state.exp_input_job_id[i]),
            key=i,
            format_func=lambda x: f"(ROME {jobs.loc[x, 'ROME']}) {jobs.loc[x, 'title']}",
            )
    (col1, col2) = st.columns(2)

    with col1:
        st.session_state.exp_input_begin[i] = st.date_input(
                "Date de début",
                key=i,
                value=st.session_state.exp_input_begin[i],
                )

    with col2:
        st.session_state.exp_input_end[i] = st.date_input(
                "Date de fin",
                key=i,
                value=st.session_state.exp_input_end[i],
                )

    st.button("Supprimer cette expérience", key=i, on_click=rm_exp_input, args=(i,))

st.button("Ajouter une expérience", on_click=add_exp_input)


update_exp_input = st.button("Mettre à jour les recommandations ci-dessous")

if not update_exp_input or 'indiv_exp' not in st.session_state:
    st.session_state.indiv_exp = m.mk_individual_experiences(
            st.session_state.exp_input_job_id,
            st.session_state.exp_input_begin,
            st.session_state.exp_input_end,
            )


st.header("On en déduit que… (changez ce que vous voulez)")

indiv_model = m.model(st.session_state.indiv_exp, jobs, jobs_skills)

with st.expander("Expériences (détails)"):
    st.table(
            indiv_model.experiences
            .assign(Nom=[jobs.loc[i, "title"] for i in indiv_model.experiences.job_id])
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
    indiv_skills_nonzero = (
            indiv_model.skills.loc[indiv_model.skills.weight > 0, :]
            .sort_values(by="weight", ascending=False)
            )

    st.table(
            indiv_skills_nonzero
            .assign(Nom=[skills.loc[i, "title"] for i in indiv_skills_nonzero.index])
            .rename(columns={"weight": "Importance"})
            .loc[:, ["Nom", "Importance"]]
    )


indiv_model.main_job = st.selectbox("Votre métier de référence est :",
        jobs.index,
        index=jobs.index.tolist().index(indiv_model.main_job),
        format_func=lambda x: f"{x}: ({jobs.loc[x, 'ROME']}) {jobs.loc[x, 'title']}"
        )

indiv_model.main_sector = st.selectbox(f"Votre secteur d'activité principal est :",
                sectors.index,
                index=sectors.index.tolist().index(indiv_model.main_sector),
                format_func=lambda x: f"{x}: ({sectors.loc[x, 'ROME']}) {sectors.loc[x, 'title']}",
                )

indiv_model.indiv_level = st.number_input("Votre niveau CEC est ",
        value = indiv_model.level,
        min_value = 1,
        max_value = 8,
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

same_sector_first = st.checkbox("Montrer d'abord les métiers du même secteur d'activité.", value = True)
hide_practiced_jobs = st.checkbox("Cacher les métiers déjà exercés.", value = True)

weigh_by_level_diff = st.checkbox(
        "Pénaliser les métiers ayant un niveau CEC supérieur au vôtre.",
        value = True)

st.write("Montrer les métiers dont le niveau CEC est entre :")

(c1, c2) = st.columns(2)

with c1:
    show_level_min = st.number_input("Valeur minimum", value=1,
                                     min_value=1, max_value=8)

with c2:
    show_level_max = st.number_input("Valeur maximum", value = 8,
                                     min_value=1, max_value=8)


n_recommended_jobs = st.number_input("Combien de métiers afficher ?", 1, 30, value=10, step=5)

job_access = m.job_accessibility(
        indiv_model,
        jobs,
        jobs_skills,
        same_sector_first,
        hide_practiced_jobs,
        weigh_by_level_diff,
        show_level_min,
        show_level_max,
        )

skill_access = m.skill_accessibility(indiv_model, skill_cooc)

job_list_markdown = ""

for j in job_access.job_accessibility.index[:n_recommended_jobs]:

    job_list_markdown += f"1. **{jobs.loc[j, 'title']}** (accessibilité du métier: {job_access.job_accessibility.loc[j]:.2f})\n"

    job_list_markdown += f"    - En raison de votre expérience pour :\n"
    for s in job_access.skill_contribution.loc[j, :].sort_values(ascending=False).loc[lambda x: x > 0].index:
        job_list_markdown += f"       - *{skills.loc[s, 'title']}*\n"

    if weigh_by_level_diff and job_access.level_diff_weights.loc[j] < 1:
        job_list_markdown += f"    - Le niveau CEC du métier est supérieur au vôtre (CEC: {jobs.loc[j, 'level']})\n"

    job_list_markdown += f"    - Vous devrez développer les compétences suivantes :\n"
    for s in job_access.skill_gap.loc[j, :].sort_values(ascending=False).loc[lambda x: x >= 1.0].index:
        sa = skill_access.skill_accessibility.loc[s]
        job_list_markdown += f"       - *{skills.loc[s, 'title']}* (accessibilité de la compétence: {sa:.2f} car vous savez déjà "
        for sc in skill_access.skill_contribution.loc[s,:].sort_values(ascending=False).loc[lambda x: x > 0].index:
            job_list_markdown += f"*{skills.loc[sc, 'title']}*; "
        job_list_markdown += ")\n"
st.write(job_list_markdown)



st.header("Les compétences à développer pour accéder à d'avantage de métiers")

with st.expander("De quoi s'agit-il ?"):
    st.write("""
    Les compétences ci-dessous sont celles qui vous aideront le plus à accéder
    à d'avantage de métiers si vous les développez.
    """)

weigh_by_job_accessibility = st.checkbox(
        "Privilégier les métiers les plus accessibles.",
        value = True)

with st.expander("Qu'est-ce que ça veut dire ?"):
    st.write("""
    En privilégiant les métiers les plus accessibles, vous verrez d'abord les
    compétences qui vous guideront vers des métiers plus
    faciles à exercer étant donné vos compétences.

    Dans le cas contraire, vous verrez aussi les compétences qui vous
    orienteront vers des métiers qui ne correspondent pas à vos compétences
    actuelles.

    Décochez cette case si vous souhaitez développer des compétences
    pour changer complètement de voie !
    """)


skill_potential = m.skill_potential(indiv_model, jobs_skills, job_access,
        weigh_by_level_diff, weigh_by_job_accessibility)

n_recommended_skills = st.number_input("Combien de compétences afficher ?", 1, 30, value=10, step=5)

markdown = ""

for s in skill_potential.average.index[:n_recommended_skills]:

    markdown += f"1. **{skills.loc[s, 'title'].strip()}**\n"
    markdown += f"    - En approfondissant cette compétence, vous augmentez l'accessibilité des métiers suivants :\n"

    jobs_with_increased_access = skill_potential.per_job.loc[s, :].sort_values(ascending=False).loc[lambda x: x > 0].index
    # jobs_with_increased_access = job_access.job_accessibility.sort_values(ascending=False).loc[lambda x: x > 0].index

    for j in jobs_with_increased_access:
        markdown += f"        - {jobs.loc[j, 'title']}\n"


st.write(markdown)
