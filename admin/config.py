from typing import Optional

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    secret: str = "unipe_secret"


config = Config()
