FROM python:3

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

COPY . /app/

CMD uvicorn api.service:app --reload --host 0.0.0.0 --port 8000

