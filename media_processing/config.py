import os


class BaseConfig:
    """Base configuration"""
    TESTING = False
    SECRET_KEY = os.environ.get("jwt_secret", "some_long_secret")
    STAGE = ""
    MICROSERVICE_NAME = "kyc-service"
    VERSION = ""


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    STAGE = "dev"


class QAConfig(BaseConfig):
    """Testing configuration"""
    STAGE = "qa"


class ProductionConfig(BaseConfig):
    """Production configuration"""
    STAGE = "prod"