# REQUIREMENTS-STAGE
FROM python:3.11-slim as requirements-stage

WORKDIR /tmp

RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN bash -c "poetry export > requirements.txt --without-hashes --with dev"


# MAIN-STAGE
FROM python:3.11-slim

ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./ /app

CMD ["python", "src/bot.py"]
