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

skills = oplc.model.model.skills

skills_jobs = oplc.model.model.jobs_skills.df.transpose()
# Remove skills that are not associated to any job
skills_jobs = skills_jobs.loc[skills_jobs.sum(axis=1) > 0, :]

experiences = (pa.DataFrame([(x.id, x.name) for x in oplc.model.model.experiences.values()],
                            columns=["id", "name"],
                            )
               .set_index("id")
              )
experiences_skills = oplc.model.model.experiences_skills.df

def run():
    indiv_exp = st.multiselect(
            "Experiences",
            experiences.index,
            default=[1,2,3],
            format_func=lambda x: f"{x}: {experiences.loc[x, 'name']}",
            )

    st.write("Expériences sélectionnées:")
    st.table(experiences.loc[indiv_exp, :])

    st.write("Compétences dérivées")
    indiv_skills = experiences_skills.loc[indiv_exp, :].sum()
    indiv_skills_nonzero = indiv_skills.loc[indiv_skills > 0]
    st.table(pa.DataFrame(
        {
         "Nom": [skills[i].name for i in indiv_skills_nonzero.index],
         "Nombre d'occurrences de la compétence dans les expériences":
            indiv_skills_nonzero,
        }
        ))


    skill_cooc = skills_jobs.dot(skills_jobs.transpose())


    st.write("Compétences de la plus accessible à la moins accessibles")


    metric = st.selectbox("Mesure de distance:", ["correlation", "cosine"], index=1)

    dist_cooc = pa.Series(np.empty(skill_cooc.shape[0]),
                          index=skill_cooc.index,
                         )


    for s in skill_cooc.index:
        not_s = (skill_cooc.index.to_series() != s).loc[lambda x: x == True].index
        dist_cooc.loc[s] = pdist([indiv_skills.loc[not_s],
                                  skill_cooc.loc[s, not_s]
                                  ],
                                 metric=metric)

    dist_cooc_sorted = dist_cooc.sort_values()
    skill_access = pa.DataFrame({
                    "Nom": [skills[i].name for i in dist_cooc_sorted.index],
                    "Distance": dist_cooc_sorted,
                    "Expériences correspondantes": indiv_skills.loc[dist_cooc_sorted.index]
                    })
    st.table(skill_access)
