import networkx as nx
import oplc.model
from oplc.core import job_recommendation, ExperienceId, JobId, JobRecommendation, SkillId
import matplotlib
import matplotlib.cm
from matplotlib import patheffects
import matplotlib.pyplot as plt
import numpy as np
import pandas as pa
import streamlit as st
from typing import Callable

experiences = [
        [
            "Maintenance électrique",
            "Montage et câblage électronique",
            "Installation et maintenance d'ascenseurs",
        ],
        [
            "Animateur / Animatrice 2D",
            "Lead graphiste - jeux vidéo",
            "UX - user experience designer",
            "UI - user interface designer",
        ],
        [
            "Manutention manuelle de charges",
            "Nettoyage de locaux",
            "Aide en puériculture",
            "Plonge en restauration",
            "Service en restauration",
            "Mise en rayon libre-service",
            "Téléconseil et télévente",
        ],
        [
            "Jardin",
            "Jeux vidéo",
            "Littérature",
            "Loisirs",
            "Mobilité",
            "Musique",
            "Médias sociaux",
            "Numérique",
            "Décoration & ameublement",
            "Famille",
            "Bande dessinée",
            "Cinéma / séries",
            "Animaux",
            "Forme & santé",
            "Recherche d'emploi",
            "Scolarité / formation",
        ],
]

measures: list[tuple[str, Callable[[nx.Graph], dict[SkillId, float]]]] = [
        ("betweenness_centrality",
         lambda g: nx.betweenness_centrality(g, endpoints=True),
         ),
        ("degree centrality",
         lambda g: nx.degree_centrality(g),
         ),
        ("closeness",
         lambda g: nx.closeness_centrality(g),
         ),
        ("eigenvector",
         lambda g: nx.eigenvector_centrality(g, tol=1e5),
         ),
        ]

# Prevent figures from being created implicitly and using memory
plt.ioff()

model = oplc.model.get()

exp_from_name = {exp.name: exp_id
                 for exp_id, exp in model.experiences.items()}


def format_experience(experience_id):
    return f"{experience_id}: {model.experiences[experience_id].name} ({model.experiences[experience_id].exp_type})"


@st.cache
def experience_ids(experience_names: list[str]):
    return [
        exp_from_name[name]
        for name in experience_names
    ]


def select_experiences(experience_ids: list[ExperienceId]):
    exps = st.multiselect(
            "Experiences sélectionnées",
            list(model.experiences.keys()),
            default=experience_ids,
            format_func=format_experience)

    return exps

def show_experiences(experience_ids):
    df = pa.DataFrame({
        "intitulé": {e: model.experiences[e].name for e in experience_ids},
        "type": {e: model.experiences[e].exp_type for e in experience_ids},
        })
    df = df.sort_index()
    st.table(df)


def show_skills(skill_ids):
    df = pa.DataFrame({
        "intitulé": {e: model.experiences[e].name for e in skill_ids},
        "type": {e: model.experiences[e].exp_type for e in skill_ids},
        })
    df = df.sort_index()
    st.table(df)


def show_job_recommendations(scores):
    st.write("Métiers recommandés (10 premiers)")
    df = pa.DataFrame({
        "intitulé": {job: model.jobs[job].name for job, score in scores.items()},
        "score": {job: score for job, score in scores.items()},
        })
    df = df.sort_index()
    st.table(df.head(10))


@st.cache(allow_output_mutation=True)
def show_graph(job_rec: JobRecommendation,
               centrality_measure: Callable[[nx.Graph], dict[JobId, float]]
               ) -> plt.Figure:
    nodes = pa.DataFrame({
        "x": {n: x for n, [x, _] in job_rec.skill_graph.layout.items()},
        "y": {n: y for n, [_, y] in job_rec.skill_graph.layout.items()},
        "centrality": centrality_measure(job_rec.skill_graph.graph),
    })

    fig, ax = plt.subplots(1, 1, figsize=(10, 7))

    for u, v in job_rec.skill_graph.graph.edges:
        if u != v:
            ax.plot(
                [nodes.loc[u, "x"], nodes.loc[v, "x"]],
                [nodes.loc[u, "y"], nodes.loc[v, "y"]],
                color="black",
                linewidth=1,
                zorder=1,
            )
    s = ax.scatter(nodes.x, nodes.y, c=nodes.centrality, s=400, zorder=2,
                   cmap="viridis")
    for x, y, e, c in zip(nodes.x, nodes.y, nodes.index, nodes.centrality):
        ax.annotate(
                str(e),
                (x, y),
                c="k",
                zorder=3,
                path_effects=[patheffects.withStroke(linewidth=3,
                                                        foreground="w")],
                horizontalalignment="center", verticalalignment="center")
    fig.colorbar(s)

    return fig


def run():

    st.title("Comparaison de mesures de centralité")

    for i, exp in enumerate(experiences):
        st.header(f"Cas de test {i+1}")
        exp_ids = select_experiences(experience_ids(exp))

        with st.expander("Voir les expériences"):
            show_experiences(exp_ids)

        st.subheader("Graphes de compétences")
        columns = st.columns(2)
        for j, (m_name, m_func) in enumerate(measures):

            job_rec = job_recommendation(
                model.experiences_skills,
                model.jobs_skills,
                exp_ids,
                return_graph=True,
                skill_centrality_measure=m_func,
            )

            with columns[j % len(columns)]:
                st.text(m_name)
                st.write(show_graph(job_rec, centrality_measure=m_func))

                with st.expander("Voir les compétences"):
                    show_skills(job_rec.skill_graph.layout.keys())



