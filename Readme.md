# Orientation par les compétences

## Project structure

- model/: A python package containing the model which computes job and skill
  recommendations
- case-studies/: A streamlit app to showcase the model
- api/: An HTTP API interface for the model
- etl/: A python package containing Extract-Transform-Load pipelines to
  preprocess the data fed to the model
- frontend/: (obsolete) a javascript/react UI for the model
- docker/: Dockerfiles to bundle everything together

## Running locally

The `case-studies/` and `api/` folders contain apps that can be run locally with
the script `up.sh` in each folder.


## Deployment in the cloud

`build.sh` builds a docker of the case-studies, the api and the frontend

`release-production.sh` sends the docker image, the file
`docker/docker-compose.yaml` and the file `.env-production` to a remote server.
The latter file must contain the following environment variables:

```
COMPOSE_PROJECT_NAME
COMPOSE_FILE
CORS_ALLOWED_ORIGINS
FRONTEND_PORT
API_PORT
API_ROOT_PATH
STREAMLIT_PORT
STREAMLIT_SERVER_BASE_URL_PATH
NEO4J_URI
NEO4J_USER
NEO4J_PASS
```

`run-production.sh` launches the services defined in `docker/docker-compose.yaml`
