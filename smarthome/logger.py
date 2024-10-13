import logging.config
from smarthome.settings import settings

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False if settings.log_level == "DEBUG" else True,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s %(funcName)s %(message)s",
        }
    },
    "handlers": {
        "default_handler": {
            "level": settings.log_level,
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "default",
        },
    },
    "root": {
        "level": "ERROR",
        "handlers": ["default_handler"]
    },
    "loggers": {
        "smarthome": {
            "handlers": ["default_handler"],
            "level": settings.log_level,
            "propagate": False,
        },
        # "sqlalchemy": {
        #     "handlers": ["default_handler"],
        #     "level": "INFO",
        #     "propagate": False,
        # },
    },
}

logging.config.dictConfig(LOG_CONFIG)

logger = logging.getLogger("smarthome")