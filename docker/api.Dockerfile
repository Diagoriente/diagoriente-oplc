FROM python:3.10

COPY api/Pipfile.lock /app/api/Pipfile.lock
COPY model/ /app/model
COPY etl/ /app/etl
WORKDIR /app/api/
RUN python -m pip install --no-cache-dir --upgrade pipenv
RUN pipenv sync

COPY api/ /app/api/

ENV API_HOST="0.0.0.0"
ENV API_PORT="8000"
ENV API_EXTRA_ARGS="--proxy-headers"

CMD ./up.sh
