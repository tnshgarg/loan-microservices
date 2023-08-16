import os
from collections import defaultdict

from dal.logger import get_app_logger


class BackgroundTask:

    def __init__(self):
        self.stage = os.environ["STAGE"]
        self.logger = get_app_logger("ops-microservice", self.stage)
        self.ops_microservice_url = os.environ["OPS_MICROSERVICE_URL"]

    def run(self, payload):
        raise ReferenceError("No handler exists")
