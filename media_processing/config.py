import os


class BaseConfig:
    """Base configuration"""

    TESTING = False
    SECRET_KEY = os.environ.get("jwt_secret", "some_long_secret")


class DevelopmentConfig(BaseConfig):
    """Development configuration"""



class TestingConfig(BaseConfig):
    """Testing configuration"""


class ProductionConfig(BaseConfig):
    """Production configuration"""
