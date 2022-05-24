import networkx as nx
import oplc.model
from oplc.core import (
        job_recommendation, ExperienceId, JobId, JobRecommendation, SkillId, jobs_from_skills,
        skill_graph,
        )
import matplotlib
import matplotlib.cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pa
import streamlit as st
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource
from sklearn.manifold import TSNE
from typing import Callable
from scipy.spatial.distance import pdist, squareform
import logging
logging.getLogger().setLevel(logging.INFO)

rng = np.random.default_rng()

plt.ioff()

sg = skill_graph(
        oplc.model.model.experiences_skills,
        list(oplc.model.model.experiences.keys()),
        )

skills = oplc.model.model.skills

# Ensure that the graph is fully connected to ensure that the dist_shortest
# matrix below has values for all pairs of nodes.
assert nx.is_connected(sg)


skills_jobs = oplc.model.model.jobs_skills.df.transpose()
# Remove skills that are not associated to any job
skills_jobs = skills_jobs.loc[skills_jobs.sum(axis=1) > 0, :]



def show_skills(dist):
    tsne = pa.DataFrame(
            TSNE(metric="precomputed", n_jobs=8).fit_transform(dist),
            index=dist.index)
    tsne = tsne.rename(columns={0: "x", 1: "y"})
    tsne.loc[:, "name"] = [skills[i].name for i in tsne.index]

    fig = figure(tools="crosshair,hover,wheel_zoom,zoom_in,zoom_out,box_zoom,reset",
                 tooltips=[("", "@name")],
                 title="Projection des compétences en 2D en respectant les distances")
    fig.scatter("x", "y", source=ColumnDataSource(data=tsne),
                fill_alpha=0.6, line_color=None, size=10)
    st.bokeh_chart(fig)

    # Take all elements except the diagonal
    dist_flat = dist.values[~np.eye(len(dist.values), dtype=bool)]
    hist, edges = np.histogram(dist_flat)
    hist_df = pa.DataFrame({"count": hist,
                            "left": edges[:-1],
                            "right": edges[1:],
                            "interval": [f"[{l}; {r}[" for l,r in zip(edges[:-1], edges[1:])]})
    fig = figure(tools="hover,box_zoom,reset", height=200,
                 tooltips=[("Distance", "@interval"),
                           ("Count", "@count")],
                 title="Distribution des distances",
                 x_axis_label="Distance",
                 y_axis_label="Nombre de paires ordonnées",
                 )
    fig.quad(left="left", right="right", top="count", bottom=0, source=hist_df)
    st.bokeh_chart(fig)


    dist_long = (dist.unstack().sort_values().reset_index()
      # Remove distances to self and redundant pairs
      .loc[lambda x: x.level_0 < x.level_1,:]
      .assign(skill1=lambda x: [skills[i].name for i in x.level_0])
      .assign(skill2=lambda x: [skills[i].name for i in x.level_1])
      .drop(columns=["level_0", "level_1"])
      .rename(columns={0: "distance"})
      )

    with st.expander(f"Compétences les plus proches"):
        st.table(dist_long.head(20))

    with st.expander(f"Compétences les plus éloignées"):
        st.table(dist_long.tail(20))


@st.cache(hash_funcs={st.delta_generator.DeltaGenerator: lambda _: None})
def dist_cooc(metric, progress_bar):
    skill_cooc = skills_jobs.dot(skills_jobs.transpose())

    dist_cooc = pa.DataFrame(np.empty(skill_cooc.shape),
                             index=skill_cooc.index,
                             columns=skill_cooc.columns,
                             )

    for i, s in enumerate(skill_cooc.index):
        progress_bar.progress(i / len(skill_cooc))
        logging.info(f"[dist_cooc] computing coocurrence between {s} and all other skills")
        for s2 in skill_cooc.columns:
            if s < s2:
                not_ij = (skill_cooc.columns != s) & (skill_cooc.columns != s2)
                dist_cooc.loc[s, s2] = pdist(skill_cooc.loc[[s,s2], not_ij],
                                            metric=metric)
            if s > s2:
                dist_cooc.loc[s, s2] = dist_cooc.loc[s2, s]
            if s == s2:
                dist_cooc.loc[s, s2] = 0

    return dist_cooc




def run():

    st.info("""
    Objectif : Comparer différentes mesures de distance entre compétences pour servir de base aux calculs d'accessibilité de métiers et de compétences.

    Démarche :
    - Pour différentes mesures de distance entre 2 compétences :
        - Calculer les distances pour toutes les paires de compétences
        - Représenter les compétences en 2D avec l'algorithme de réduction de dimensions t-SNE
        - Évaluer les résultats à l'œil pour obtenir une première idée des qualités des distances
    - On teste 3 approches pour calculer les distances : la première basée sur le graphe de coocurrence de compétences, la seconde sur une comparaison des compétences en termes de métiers auxquelles elles sont rattachées, la troisième sur une comparaison des compétences en termes de compétences avec lesquelles elles sont associées par le biais des métiers. La 2e et la 3e approche passent par une représentation des compétences en vecteur (vecteurs de métiers associés pour la 2e et vecteurs de compétences associées pour la 3e). Elles sont mises en œuvre avec plusieurs mesures de distance entre vecteurs (euclidienne, corrélation, cosinus).

    Résultats :
    - Certaines méthodes produisent des groupes de compétences cohérentes, les groupes étant séparés les uns des autres. Les meilleurs exemples sont ceux de l'approche 3 avec les distances corrélation et cosinus. Cet effet d'augmenter la distance entre compétences non liées pourrait nous aider à éviter les recommandations aberrantes.
    - La première approche basée sur le chemin plus court donne une distance qui manque de finesse. L'histogramme des distances montre seulement 3 valeurs de distance possibles: 1, 2 ou 3. Toutes les compétences sont à 1, 2 ou 3 pas de toutes les autres dans le graphe. Cela limite la possibilité de distinguer des groupes: les compétences sont à une distance de 2 de la plupart des autres. Pour celles qui sont proches (distance de 1), on ne peut pas faire la différence entre celles qui ont un métier en commun et celles qui ont de nombreux métiers en commun.
    - Dans les approches 2 et 3, la distance euclidienne produit des distances avec une distribution en cloche, alors que les distances de corrélation et cosinus ont des distributions beaucoup plus asymmétriques. C'est peut-être ce qui offre dans l'approche 2 et 3 cet effet de groupe reserrés et bien séparés les uns des autres: les compétences sont d'avantage éloignées de la plupart des compétences sauf de celles du même groupe, ce qui donne quelques petites distances et de nombreuses grandes distances. L'absence de cet effet avec la distance euclidienne est peut-être une conséquence du fléau de la dimensionalité.
    - L'effet groupe est intéressant car il identifie plus clairement des compétences proches et des compétences éloignées et évite de nombreuses distances intermédiaires, que l'on observe beaucoup plus avec l'approche 1 ou la distance euclidienne.
    """)


    st.header("Approche 1: Longueur du chemin le plus court entre deux compétences dans le graphe de compétences")

    dist_shortest = pa.DataFrame({u: d for u,d in nx.all_pairs_shortest_path_length(sg)}).sort_index()

    show_skills(dist_shortest)



    st.header("Approche 2: On compare les compétences par rapport aux métiers auxquelles elles sont rattachées.")
    st.write("Chaque compétence est représentée par un vecteur booléen de taille égale au nombre de métiers où un élément vaut vrai si la compétence est rattachée au métier correspondant.")

    st.subheader("Distance euclidienne entre les vecteurs")

    dist_jobs_euclidean = pa.DataFrame(
            squareform(pdist(skills_jobs, metric="euclidean")),
            index=skills_jobs.index,
            columns=skills_jobs.index,
            )
    show_skills(dist_jobs_euclidean)



    st.subheader("Distance de corrélation entre les vecteurs")

    dist_jobs_correlation = pa.DataFrame(
            squareform(pdist(skills_jobs, metric="correlation")),
            index=skills_jobs.index,
            columns=skills_jobs.index,
            )
    show_skills(dist_jobs_correlation)



    st.subheader("Distance cosinus entre les vecteurs")

    dist_jobs_correlation = pa.DataFrame(
            squareform(pdist(skills_jobs, metric="cosine")),
            index=skills_jobs.index,
            columns=skills_jobs.index,
            )
    show_skills(dist_jobs_correlation)



    st.header("Approche 3: On compare les compétences par rapport aux compétences avec lequelles elles sont associées")
    st.write("Chaque compétence est représentée par un vecteur d'entiers de taille égale au nombre de compétences où un élément est égal au nombre de fois que la compétence est associée à la compétence correspondante dans les métiers.")
    st.write("Avant de calculer la distance (euclidienne, correlation, etc) entre deux compétences i et j, on supprime des deux vecteurs associés les éléments en position i et j. Ces éléments correspondent au nombre de fois qu'une compétence est associée à elle-même. Ces valeurs sont naturellement grandes et ont trop de poids dans les calculs si on les laisse, écrasant les autres valeurs qui portent pourtant plus d'information.")

    st.subheader("Distance euclidienne")
    progress = st.progress(0)
    dist_cooc_euclidean = dist_cooc("euclidean", progress)
    progress.progress(1.0)
    show_skills(dist_cooc_euclidean)

    st.subheader("Distance de corrélation")
    progress = st.progress(0)
    dist_cooc_correlation = dist_cooc("correlation", progress)
    progress.progress(1.0)
    show_skills(dist_cooc_correlation)

    st.subheader("Distance cosinus")
    progress = st.progress(0)
    dist_cooc_cosine = dist_cooc("cosine", progress)
    progress.progress(1.0)
    show_skills(dist_cooc_cosine)
