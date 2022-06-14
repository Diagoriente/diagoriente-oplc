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
    edges = []

    with driver.session() as session:
        result = session.read_transaction(_get_job_skill_graph)
        for (job_id, job_title, job_rome),(skill_id, skill_title) in result:
            jobs[job_id] = job_title
            skills[skill_id] = skill_title
            edges.append((job_id, skill_id))

    jobs_skills = pa.DataFrame(
            np.zeros((len(jobs), len(skills)), dtype=int),
            columns=skills.keys(),
            index=jobs.keys(),
            )

    for (j,s) in edges:
        jobs_skills.loc[j, s] = 1

    return jobs, skills, jobs_skills


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
    result = None

    with driver() as d:
        result = get_job_skill_data(d)

    return result
