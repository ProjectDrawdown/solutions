FROM python:3.8.7

ENV PATH=$PATH:/usr/local/bin:/env/bin
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

RUN mkdir /app
COPY . /app/
WORKDIR /app

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000

CMD alembic upgrade head && uvicorn api.service:app --reload --host 0.0.0.0 --port 8000
