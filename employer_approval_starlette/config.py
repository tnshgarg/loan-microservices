from typing import Optional

from pydantic import BaseSettings


class Config(BaseSettings):
    secret: str = "unipe_secret"


config = Config()
