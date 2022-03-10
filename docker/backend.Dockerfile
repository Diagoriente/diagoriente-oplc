FROM python:3.9

COPY ./backend/python/requirements.txt /app/backend/requirements.txt
WORKDIR /app/
RUN python -m pip install --no-cache-dir --upgrade -r backend/requirements.txt

COPY backend/python /app

CMD ["uvicorn", "oplc.api:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
