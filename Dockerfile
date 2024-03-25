FROM python:3.9-slim

RUN mkdir -p /opt/dagster/app /opt/dagster/app/data

COPY workspace.yaml pyproject.toml .python-version Makefile dagster.yaml /opt/dagster/app/
COPY src /opt/dagster/app/src
COPY .env_docker /opt/dagster/app/.env

WORKDIR /opt/dagster/app

ENV PYTHONPATH=${PYTHONPATH}:${PWD}
ENV PYTHONUNBUFFERED True

RUN apt-get update && apt-get install -y make && apt-get install -y git && apt-get install -y curl

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --only main
RUN poetry install --with dev

EXPOSE 3000

CMD ["poetry", "run", "dagster", "dev", "-h", "0.0.0.0"]
