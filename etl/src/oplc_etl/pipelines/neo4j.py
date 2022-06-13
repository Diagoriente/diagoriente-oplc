import os
import numpy as np
import pandas as pa
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from contextlib import contextmanager

neo4jURI=os.getenv("NEO4J_URI")
neo4jUser=os.getenv("NEO4J_USER")
neo4jPass=os.getenv("NEO4J_PASS")

@contextmanager
def driver(uri=neo4jURI,
           user=neo4jUser,
           password=neo4jPass):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    yield driver
    driver.close()


def get_job_skill_data(driver):
    jobs = {}
    skills = {}
    experiences = {}
    edges = []

    with driver.session() as session:
        result = session.read_transaction(_get_job_skill_graph)
        for (job_id, job_title, job_rome),(skill_id, skill_title) in result:
            jobs[job_id] = job_title
            skills[skill_id] = skill_title
            #TODO: qu'est-ce qu'on fait du type d'expérience ?
            experiences[job_id] = (job_title, "pro")
            edges.append((job_id, skill_id))

    experiences_skills = pa.DataFrame(
            np.zeros((len(experiences), len(skills)), dtype=int),
            columns=skills.keys(),
            index=experiences.keys(),
            )

    jobs_skills = pa.DataFrame(
            np.zeros((len(jobs), len(skills)), dtype=int),
            columns=skills.keys(),
            index=jobs.keys(),
            )

    for (j,s) in edges:
        experiences_skills.loc[j, s] = 1
        jobs_skills.loc[j, s] = 1

    return jobs, skills, experiences, experiences_skills, jobs_skills


def _get_job_skill_graph(tx):
    query = (
        "MATCH (j:Job)-[r:HasCompetency]-(c:Competences) "
        "RETURN j,c"
    )
    result = tx.run(query)

    return [
        ((row["j"].id, row["j"]["title"], row["j"]["ROME"]),
         (row["c"].id, row["c"]["title"]))
        for row in result
    ]


def get_data():
    global driver

    with driver() as driver:
        return get_job_skill_data(driver)
