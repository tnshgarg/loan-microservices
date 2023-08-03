import os


def get_ops_microservice_url():
    ops_microservice_url = os.environ["ops_microservice_url"]
    return ops_microservice_url
