from typing import Optional

from pydantic import BaseSettings


class Config(BaseSettings):
    mongo_uri: str = "mongodb+srv://aws_lambda_dev:15HYlXJ3wG0821WD@cluster1.sebmken.mongodb.net/dev?retryWrites=true&w=majority"
    mongo_db: str = "dev"
    secret: str = "unipe_secret"


config = Config()
