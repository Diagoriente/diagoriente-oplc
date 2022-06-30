FROM python:3.10

COPY ui/Pipfile.lock /app/ui/Pipfile.lock
COPY model /app/model
COPY etl /app/etl
WORKDIR /app/ui
RUN python -m pip install --no-cache-dir --upgrade pipenv
RUN pipenv sync

COPY ui /app/ui

ENV PYTHONPATH "."

ENV STREAMLIT_HOST="0.0.0.0"
ENV STREAMLIT_PORT="8501"

CMD ./up.sh
