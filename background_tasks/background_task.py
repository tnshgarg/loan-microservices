import os
from collections import defaultdict

from dal.logger import get_app_logger


class BackgroundTask:

    def __init__(self):
        self.stage = os.environ["stage"]
        self.logger = get_app_logger("ops-microservice", self.stage)
        self.ops_microservice_url = os.environ["ops_microservice_url"]

    def run(self, payload):
        raise ReferenceError("No handler exists")
