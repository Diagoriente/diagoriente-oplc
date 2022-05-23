import networkx as nx
import oplc.model
from oplc.core import (
        job_recommendation, ExperienceId, JobId, JobRecommendation, SkillId,
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

plt.ioff()

sg = skill_graph(
        oplc.model.model.experiences_skills,
        list(oplc.model.model.experiences.keys()),
        )

skills = oplc.model.model.skills

# Ensure that the graph is fully connected to ensure that the dist_shortest
# matrix below has values for all pairs of nodes.
assert nx.is_connected(sg)





def show_skills(dist):
    tsne = pa.DataFrame(
            TSNE(metric="precomputed", n_jobs=8).fit_transform(dist),
            index=dist.index)
    tsne = tsne.rename(columns={0: "x", 1: "y"})
    tsne.loc[:, "name"] = [skills[i].name for i in tsne.index]

    fig = figure(tools="crosshair,hover,wheel_zoom,zoom_in,zoom_out,box_zoom,reset",
                 tooltips=[("", "@name")])
    fig.scatter("x", "y", source=ColumnDataSource(data=tsne),
                fill_alpha=0.6, line_color=None, size=10)
    st.bokeh_chart(fig)


    dist_long = (dist.unstack().sort_values().reset_index()
      .loc[lambda x: x.level_0 != x.level_1,:]
      .assign(skill1=lambda x: [skills[i].name for i in x.level_0])
      .assign(skill2=lambda x: [skills[i].name for i in x.level_1])
      .drop(columns=["level_0", "level_1"])
      .rename(columns={0: "distance"})
      )


    with st.expander("Exemples de compétences proches"):
        st.table(dist_long.head(20))

    with st.expander("Exemples de compétences éloignées"):
        st.table(dist_long.tail(20))



def run():
    st.header("Distance: chemin plus court")

    dist_shortest = pa.DataFrame({u: d for u,d in nx.all_pairs_shortest_path_length(sg)}).sort_index()

    show_skills(dist_shortest)



    st.header("Distance: similarité des métiers")

    skills_jobs = oplc.model.model.jobs_skills.df.transpose()
    skills_jobs = skills_jobs.loc[skills_jobs.sum(axis=1) > 0, :]
    dist_jobs_dot_product = 1 / (1 + skills_jobs.dot(skills_jobs.transpose()))
    show_skills(dist_jobs_dot_product)



    st.header("Distance: similarité des métiers (vecteurs normés)")

    skills_jobs_norm = skills_jobs.div(skills_jobs.sum(axis=1), axis=0)
    skills_jobs_norm = skills_jobs_norm.dropna()
    dist_jobs_dot_norm = 1 / (1 + skills_jobs_norm.dot(skills_jobs_norm.transpose()))
    show_skills(dist_jobs_dot_norm)



# fig, ax = plt.subplots(figsize=(10,10))
# for i in tsne_shortest.index:
#     ax.text(tsne_shortest.loc[i, 0], tsne_shortest.loc[i, 1], skills[i].name, 
#             fontsize=10)
# ax.set_xlim(tsne_shortest.loc[:, 0].min(), tsne_shortest.loc[:, 0].max())
# ax.set_ylim(tsne_shortest.loc[:, 1].min(), tsne_shortest.loc[:, 1].max())
# plt.show()
# 
# fig, ax = plt.subplots(figsize=(10,10))
# ax.scatter(tsne_job_sim[:, 0], tsne_job_sim[:, 1])
# plt.show()
