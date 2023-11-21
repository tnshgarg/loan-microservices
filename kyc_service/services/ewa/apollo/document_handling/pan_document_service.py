

from io import BytesIO
import json
from bson import ObjectId
import requests

from dal.models.encrypted_government_ids import EncryptedGovernmentIds
from kyc_service.config import Config


class PANStatusCheckService:

    def __init__(self, unipe_employee_id: ObjectId):
        self.pan_doc = EncryptedGovernmentIds.find_one({
            "pId": unipe_employee_id,
            "type": "pan",
            "provider": "karza",
            "verifyStatus": "SUCCESS"
        })
        self.pan_data = self.pan_doc["karzaResponse"]["result"]
        self.unipe_employee_id = unipe_employee_id
        self.karza_assets = Config.KARZA
        self.KARZA_API_KEY = self.karza_assets.get("api_key")
        self.KARZA_BASE_URL = self.karza_assets.get("base_url")

    def generate_document(self) -> BytesIO:
        endpoint_url = f"{self.KARZA_BASE_URL}/v2/pan-authentication"
        headers = {
            "x-karza-key": self.KARZA_API_KEY
        }
        payload = {
            "consent": "Y",
            "pan": self.pan_data["pan"],
            "name": self.pan_data["name"],
            "dob": "/".join(reversed(self.pan_data["dob"].split("-"))),
        }

        response = requests.post(
            url=endpoint_url,
            headers=headers,
            json=payload
        )
        EncryptedGovernmentIds.update_one({"_id": self.pan_doc["_id"]}, {
            "$set": {"karzaStatusCheck": response.json()}
        })
        return BytesIO(response.content)
