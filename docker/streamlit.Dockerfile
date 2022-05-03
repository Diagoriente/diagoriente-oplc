FROM python:3.10

COPY ./Pipfile.lock /app/Pipfile.lock
WORKDIR /app/
RUN python -m pip install --no-cache-dir --upgrade pipenv
RUN pipenv sync

COPY backend/python /app
COPY case-studies /app/case-studies

ENV PYTHONPATH "."

CMD ["pipenv", "run", "streamlit", "run", "case-studies/main.py", "--server.port", "8501"]
