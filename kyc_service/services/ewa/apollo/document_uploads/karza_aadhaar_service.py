

from base64 import b64decode
from io import BytesIO
from bson import ObjectId

from dal.models.encrypted_government_ids import EncryptedGovernmentIds


class AadhaarZipService:

    def __init__(self, unipe_employee_id: ObjectId) -> None:
        self.aadhaar_data = EncryptedGovernmentIds.find_one({
            "pId": unipe_employee_id,
            "type": "aadhaar",
            "provider": "karza",
            "verifyStatus": "SUCCESS"
        })

    def generate_document(self) -> BytesIO:
        base64_zip_file = self.aadhaar_data["karzaResponse"]["result"]["dataFromAadhaar"]["file"]
        return BytesIO(b64decode(base64_zip_file))
