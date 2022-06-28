import os
from pathlib import Path
import numpy as np
import pandas as pa
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from contextlib import contextmanager
from dataclasses import dataclass

import logging

neo4jURI=os.getenv("NEO4J_URI")
neo4jUser=os.getenv("NEO4J_USER")
neo4jPass=os.getenv("NEO4J_PASS")

default_cache_dir = Path("/tmp/diagoriente-oplc/data")


def download_data_to_disk(dir: Path = default_cache_dir):
    result = get_data(cache_dir=None)

    dir.mkdir(parents=True, exist_ok=True)

    result.jobs.to_csv(dir/"jobs.csv")
    result.skills.to_csv(dir/"skills.csv")
    result.sectors.to_csv(dir/"sectors.csv")
    result.jobs_skills.to_csv(dir/"jobs_skills.csv")


def get_data(cache_dir: Path | None = None):
    result = None

    if cache_dir is None:
        with driver() as d:
            result = get_job_skill_data(d)
    else:
        result = Result(
                jobs=pa.read_csv(cache_dir/"jobs.csv"),
                skills=pa.read_csv(cache_dir/"skills.csv"),
                sectors=pa.read_csv(cache_dir/"sectors.csv"),
                jobs_skills=pa.read_csv(cache_dir/"jobs_skills.csv"),
                )

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
        for (job_id, job_title, job_rome, job_level_label) in result_jobs:

            job_level = job_level_from_label(job_level_label)

            valid = True

            if job_level is None:
                valid = False
                logging.warning(
                    f"Dropping job {job_id} {job_rome} {job_title} "
                    f"because its job level is {job_level_label}")

            if valid:
                jobs[job_id] = {"job": job_id, "title": job_title, "ROME": job_rome,
                                "level": job_level}

        result_skills = session.read_transaction(_get_skills_data)
        for (skill_id, skill_title) in result_skills:
            skills[skill_id] = {"skill": skill_id, "title": skill_title}

        result_sectors = session.read_transaction(_get_sectors_data)
        for (sector_id, sector_title, sector_rome) in result_sectors:
            sectors[sector_id] = {"sector": sector_id, "title": sector_title, "ROME": sector_rome}

        result_job_skill = session.read_transaction(_get_job_skill_graph)
        for (job_id, skill_id) in result_job_skill:

            valid = True

            if job_id not in jobs.keys():
                valid = False
                logging.warning(
                    f"Dropping job {job_id} from job_skill because it is absent"
                    f" from known jobs.")

            if skill_id not in skills.keys():
                valid = False
                logging.warning(
                    f"Dropping skill {skill_id} from job_skill because it is absent"
                    f" from known skills.")

            if valid:
                edges.append((job_id, skill_id))

        result_job_sector = session.read_transaction(_get_job_sector_map)
        for (job_id, sector_id) in result_job_sector:

            valid = True

            if job_id not in jobs:
                valid = False
                logging.warning(
                    f"Could not find job {job_id} while trying to attribute "
                    f"sector {sector_id} to it.")

            if valid:
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
        if j in jobs.index and s in skills.index:
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
    return [(row["j"].id, row["j"]["title"], row["j"]["ROME"], row["j"]["Level"]) for row in result]


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


def job_level_from_label(label):
    if label == 'NIV1':
        return 1
    elif label == 'NIV2':
        return 2
    elif label == 'NIV3':
        return 3
    elif label == 'NIV4':
        return 4
    elif label == 'NIV5':
        return 5
    elif label == 'NIV6':
        return 6
    elif label == 'NIV7':
        return 7
    elif label == 'NIV8':
        return 8
    else:
        return None
