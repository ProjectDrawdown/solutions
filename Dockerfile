FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH=$PATH:/usr/local/bin

RUN mkdir /app
WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt

CMD uvicorn api.service:app --reload --host 0.0.0.0 --port 8000

