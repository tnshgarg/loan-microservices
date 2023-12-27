import bson
from datetime import datetime
from admin.apis.karza_api import KarzaApi
from dal.models.encrypted_government_ids import EncryptedGovernmentIds


class KarzaKycService:

    def __init__(self, logger, stage, use_mock=False) -> None:
        super().__init__()
        self.logger = logger
        self.stage = stage
        self.karza_api = KarzaApi()

    def pan_fetch_details(self, p_id, pan_number, u_type="employee"):
        filter_ = {
            "pId": p_id,
            "type": "pan",
            "uType": u_type,
            "provider": "karza"
        }
        try:
            pan_fetch_details_response = self.karza_api.pan_fetch_details(
                pan_number=pan_number
            )
            data = pan_fetch_details_response
            if data.get("statusCode") == 101:
                pan_data = data["result"]
                pan_address = ", ".join(pan_data["address"].values())
                EncryptedGovernmentIds.update_one(
                    filter_,
                    {
                        "$set": {
                            "number": pan_number,
                            "verifyStatus": "INPROGRESS_CONFIRMATION",
                            "verifyMsg": data.get("result").get("status"),
                            "data": {
                                "pan": pan_data["pan"],
                                "name": pan_data["name"],
                                "firstName": pan_data["firstName"],
                                "middleName": pan_data["middleName"],
                                "lastName": pan_data["lastName"],
                                "gender": pan_data["gender"],
                                "date_of_birth": pan_data["dob"],
                                "address": pan_address
                            },
                            "verifyTimestamp": pan_fetch_details_response.get("timestamp"),
                            "karzaResponse": data,
                            "validFor": ['apollo', 'liquiloans'],
                            "provider": "karza"
                        }
                    }
                )

                return {
                    "status": 200,
                    "body": {
                        "verifyStatus": "INPROGRESS_CONFIRMATION",
                        "message": data.get("result").get("status"),
                        "data": data.get("result"),
                        "provider": "karza"
                    }
                }
            else:
                EncryptedGovernmentIds.update_one(
                    filter_,
                    {
                        "$set": {
                            "verifyStatus": "ERROR",
                            "verifyMsg": "An Error Occured while verifying your PAN, Please Try Again!",
                            "verifyTimestamp": int(datetime.now().timestamp()),
                            "provider": "karza"
                        }
                    }
                )
                return {
                    "status": 400,
                    "body": {
                        "verifyStatus": "ERROR",
                        "message": "An Error Occured while verifying your PAN, Please Try Again!",
                    }
                }

        except Exception as e:
            EncryptedGovernmentIds.update_one(
                filter_,
                {
                    "$set": {
                        "verifyStatus": "ERROR",
                        "verifyMsg": str(e),
                        "verifyTimestamp": int(datetime.now().strftime('%s')),
                        "provider": "karza"
                    }
                }
            )
            raise e
