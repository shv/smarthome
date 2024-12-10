"""
Settings
"""
import logging
# from typing import Any, Callable, Set

# from pydantic import (
#     AliasChoices,
#     AmqpDsn,
#     BaseModel,
#     Field,
#     ImportString,
#     PostgresDsn,
#     RedisDsn,
# )

from pydantic_settings import BaseSettings, SettingsConfigDict


# class SubModel(BaseModel):
#     foo: str = "bar"
#     apple: int = 1


class Settings(BaseSettings):
    """ All settings """
    log_level: str = "DEBUG"
    # auth_key: str = Field(validation_alias="my_auth_key")

    main_url: str = ""

    pg_dsn: str = "postgresql://smarthome:smarthome123@localhost:5435/smarthome_dev"

    redis_host: str = "127.0.0.1"
    redis_port: int = 6380
    # api_key: str = Field(alias="my_api_key")
    # redis_dsn: RedisDsn = Field(
    #     "redis://user:pass@localhost:6379/1",
    #     validation_alias=AliasChoices("service_redis_dsn", "redis_url"),
    # )
    # amqp_dsn: AmqpDsn = "amqp://user:pass@localhost:5672/"

    # special_function: ImportString[Callable[[Any], Any]] = "math.cos"

    # to override domains:
    # export my_prefix_domains="["foo.com", "bar.com"]"
    # domains: Set[str] = set()

    # to override more_settings:
    # export my_prefix_more_settings="{"foo": "x", "apple": 1}"
    # more_settings: SubModel = SubModel()

    model_config = SettingsConfigDict(env_prefix="smarthome_bak_")


settings = Settings()
