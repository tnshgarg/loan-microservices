

from io import BytesIO
import json
from bson import ObjectId
import requests

from dal.models.employees import Employee


class LivenessCheckService:

    def __init__(self, unipe_employee_id: ObjectId) -> None:
        self.profile = Employee.find_one({"_id": unipe_employee_id})

    def generate_document(self) -> BytesIO:
        liveness_check_bytes = json.dumps(
            self.profile["liveness"]).encode()
        return BytesIO(liveness_check_bytes)

    def get_selfie(self) -> BytesIO:
        r = requests.get(
            url=self.profile["profile_pic"]["aws_url"],
            allow_redirects=True
        )
        if r.status_code == 200:
            return BytesIO(r.content)
