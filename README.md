## Setup

*Custom venv*

`python -m pip install pip setuptools --upgrade`

`python -m pip install poetry`

`poetry install`

*With global poetry*

`poetry shell`

`poetry install`

## ENV

`export SMARTHOME_BAK_MAIN_URL=/v1`

## Run

`poetry run uvicorn smarthome.main:app --reload --port 8000`

## Tests

`poetry run pytest`

## Linters

`poetry run mypy ./`
`poetry run pylint ./smarthome`

## Docker

`docker build . --tag smarthome`

`docker run -p 8000:8000 --env SMARTHOME_BAK_MAIN_URL=/v1 smarthome`

## Compose

# Run prod

```bash
docker compose up -d prod
```

## Literature

# https://pypi.org/project/fastapi-socketio/
# https://python-socketio.readthedocs.io/en/stable/

# ESP32 simulator
# https://wokwi.com/

# ESP32 Examples

# https://github.com/gilmaimon/ArduinoWebsockets/blob/master/README.md
# https://github.com/gilmaimon/ArduinoWebsockets/blob/master/examples/Esp8266-Server/Esp8266-Server.ino

# https://github.com/larkin/ESP32-Websocket/blob/master/README.md

# https://docs.espressif.com/projects/esp-idf/en/v4.4.2/esp32/api-reference/protocols/esp_websocket_client.html
