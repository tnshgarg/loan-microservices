

from io import BytesIO
import json
from bson import ObjectId

from dal.models.encrypted_government_ids import EncryptedGovernmentIds


class PANStatusCheckService:

    def __init__(self, unipe_employee_id: ObjectId):
        self.pan_data = EncryptedGovernmentIds.find_one({
            "pId": unipe_employee_id,
            "type": "pan",
            "provider": "karza",
            "verifyStatus": "SUCCESS"
        })
        self.aadhaar_data = EncryptedGovernmentIds.find_one({
            "pId": unipe_employee_id,
            "type": "aadhaar",
            "provider": "karza",
            "verifyStatus": "SUCCESS"
        })

    def generate_document(self) -> BytesIO:
        pan_status_check = self.pan_data["karzaResponse"]
        status_check_bytes = json.dumps(pan_status_check).encode()
        return BytesIO(status_check_bytes)
