FROM python:3.13.0-alpine

EXPOSE 8000

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1 PYTHONUNBUFFERED 1

RUN pip install --upgrade pip && apk add gcc musl-dev libffi-dev &&  \
    pip install --upgrade setuptools && pip install --upgrade poetry

COPY poetry.lock pyproject.toml /code/

ARG POETRY_DEV_INSTALL=false

RUN poetry config virtualenvs.create false && \
    if [ "$POETRY_DEV_INSTALL" = "true" ]; then \
      poetry install --no-interaction --no-ansi --with dev; \
    else \
      poetry install --no-interaction --no-ansi --without dev; \
    fi

COPY . /code

CMD ["poetry", "run", "uvicorn", "smarthome.main:app", "--host", "0.0.0.0", "--port", "8001"]
