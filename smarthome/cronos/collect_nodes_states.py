"""
Добавлено в локальный crontab на каждую минуту
"""
import httpx
from smarthome import cruds, models, schemas
from smarthome.depends import get_db
from smarthome.logger import logger


def main() -> None:
    logger.info("Start collect nodes states request")
    with next(get_db()) as db_session:
        # TODO: Заменить на crud
        nodes = db_session.query(models.Node).filter(models.Node.url.is_not(None), models.Node.is_active).all()
        for node in nodes:
            result = httpx.get(node.url)
            if result.status_code != 200:
                logger.error("ERROR: %s", result.status_code)
                return

            response_data = result.json()
            if "error" in response_data:
                logger.error("ERROR from ESP32: %s", response_data["error"])
                return

            logger.info("DATA from ESP32 #%s: %s", node.id, response_data)

            # Сюда пишем полный ответ ноды
            cruds.create_node_state(db_session, schemas.NodeStateCreate(data=response_data, node_id=node.id))

            # А тут работаем уже с данными от нее
            data = response_data.get("data", {})

            for key, value in data.items():
                cruds.upsert_node_current_values(db_session, node.id, schemas.NodeCurrentValueCreate(name=key, value=value))

            logger.info("DATA from ESP32 #%s received", node.id)


if __name__ == '__main__':
    main()
