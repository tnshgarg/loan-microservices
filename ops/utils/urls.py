import os


def get_ops_microservice_url():
    ops_microservice_url = os.environ["OPS_MICROSERVICE_URL"]
    return ops_microservice_url
