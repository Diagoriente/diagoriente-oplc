FROM python:3.10

COPY case-studies/Pipfile.lock /app/case-studies/Pipfile.lock
COPY model /app/model
COPY etl /app/etl
WORKDIR /app/case-studies
RUN python -m pip install --no-cache-dir --upgrade pipenv
RUN pipenv sync

COPY case-studies /app/case-studies

ENV PYTHONPATH "."

ENV STREAMLIT_HOST="0.0.0.0"
ENV STREAMLIT_PORT="8501"

CMD ./up.sh
