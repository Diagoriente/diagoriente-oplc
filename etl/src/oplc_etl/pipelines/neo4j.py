import os
import numpy as np
import pandas as pa
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from contextlib import contextmanager
from dataclasses import dataclass

neo4jURI=os.getenv("NEO4J_URI")
neo4jUser=os.getenv("NEO4J_USER")
neo4jPass=os.getenv("NEO4J_PASS")


def get_data():
    result = None

    with driver() as d:
        result = get_job_skill_data(d)

    return result


@contextmanager
def driver(uri=neo4jURI,
           user=neo4jUser,
           password=neo4jPass):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    yield driver
    driver.close()



@dataclass
class Result:
    jobs: pa.DataFrame
    skills: pa.DataFrame
    sectors: pa.DataFrame
    jobs_skills: pa.DataFrame


def get_job_skill_data(driver):
    jobs = {}
    skills = {}
    sectors = {}
    edges = []

    with driver.session() as session:
        result_jobs = session.read_transaction(_get_jobs_data)
        for (job_id, job_title, job_rome) in result_jobs:
            jobs[job_id] = {"job": job_id, "title": job_title, "ROME": job_rome}

        result_skills = session.read_transaction(_get_skills_data)
        for (skill_id, skill_title) in result_skills:
            skills[skill_id] = {"skill": skill_id, "title": skill_title}

        result_sectors = session.read_transaction(_get_sectors_data)
        for (sector_id, sector_title, sector_rome) in result_sectors:
            sectors[sector_id] = {"sector": sector_id, "title": sector_title, "rome": sector_rome}

        result_job_skill = session.read_transaction(_get_job_skill_graph)
        for (job_id, skill_id) in result_job_skill:
            edges.append((job_id, skill_id))

        result_job_sector = session.read_transaction(_get_job_sector_map)
        for (job_id, sector_id) in result_job_sector:
            jobs[job_id]["sector"] = sector_id

    jobs = pa.DataFrame(jobs.values()).set_index("job")
    skills = pa.DataFrame(skills.values()).set_index("skill")
    sectors = pa.DataFrame(sectors.values()).set_index("sector")

    jobs_skills = pa.DataFrame(
            np.zeros((len(jobs), len(skills)), dtype=int),
            columns=skills.index,
            index=jobs.index,
            )

    for (j,s) in edges:
        jobs_skills.loc[j, s] = 1

    return Result(
            jobs=jobs,
            skills=skills,
            sectors=sectors,
            jobs_skills=jobs_skills,
            )


def _get_jobs_data(tx):
    query = (
        "MATCH (j:Sous_Domaine) "
        "return j"
    )
    result = tx.run(query)
    return [(row["j"].id, row["j"]["title"], row["j"]["ROME"]) for row in result]


def _get_skills_data(tx):
    query = (
        "MATCH (c:Competence) "
        "return c"
    )
    result = tx.run(query)
    return [(row["c"].id, row["c"]["title"]) for row in result]


def _get_sectors_data(tx):
    query = (
        "MATCH (j:Secteur) "
        "return j"
    )
    result = tx.run(query)
    return [(row["j"].id, row["j"]["title"], row["j"]["ROME"]) for row in result]


def _get_job_skill_graph(tx):
    query = (
        "MATCH (j:Sous_Domaine)-[r:HasCompetence]-(c:Competence) "
        "RETURN j,c"
    )
    result = tx.run(query)
    return [(row["j"].id,row["c"].id) for row in result]


def _get_job_sector_map(tx):
    query = (
        "MATCH (j:Sous_Domaine)-[:HasSous_Domaine]-(:Domaine)-[:HasDomaine]-(c:Secteur) "
        "return j, c"
    )
    result = tx.run(query)
    return [(row["j"].id, row["c"].id) for row in result]



