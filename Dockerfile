FROM python:3.6

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt

CMD uvicorn api.service:app --reload --host 0.0.0.0 --port 8000

