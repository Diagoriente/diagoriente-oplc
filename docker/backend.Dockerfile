FROM python:3.9

COPY ./Pipfile.lock /app/Pipfile.lock
WORKDIR /app/
RUN python -m pip install --no-cache-dir --upgrade pipenv
RUN pipenv sync


COPY backend/python /app

CMD ["pipenv", "run", "uvicorn", "oplc.api:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
