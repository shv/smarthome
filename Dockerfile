FROM python:3.12.2-alpine

EXPOSE 8000

WORKDIR /code

RUN pip install --upgrade pip
RUN apk add gcc musl-dev libffi-dev
RUN pip install poetry

COPY . /code

RUN poetry config virtualenvs.create true \
    && poetry install --no-interaction --no-ansi

CMD ["poetry", "run", "uvicorn", "smarthome.main:app", "--host", "0.0.0.0", "--port", "8000", "--ws-ping-interval", "10", "--ws-ping-timeout", "10"]
#CMD ["poetry", "run", "pytest"]