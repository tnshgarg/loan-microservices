
import json
import os

from services.otp.gupshup.gupshup_api import GupshupApi


class GupshupApiMock(GupshupApi):
    def __init__(self, logger) -> None:
        self.logger = logger

        self.gupshup_assets = json.loads(
            os.environ.get("gupshup_secret", "{}"))
        self.base_url = self.gupshup_assets.get("base_url")
        # print("baseurl: ", self.base_url)
        self.gupshup_userid = self.gupshup_assets.get("userid")
        self.gupshup_password = self.gupshup_assets.get("password")
        self.otp_string = self.gupshup_assets.get("otp_message_string")
        self.headers = {
            "Content-Type": "application/json",
        }

    def merge_url(self, val):
        return val + "=" + self.params[val]

    def generate_otp(self, mobile_number: str):
        return {
            "response": {
                "id": "4915879563758850070",
                "phone": f"91{mobile_number}",
                "details": "OTP sent.",
                "status": "success"
            }
        }

    def verify_otp(self, mobile_number: str, otp: str):
        if otp == "999999":
            return {
                "response": {
                    "id": "310",
                    "phone": "",
                    "details": "This OTP is incorrect.",
                    "status": "error"
                }
            }
        if otp == "888888":
            return {
                "response": {
                    "id": "301",
                    "phone": "",
                    "details": "OTP token has expired.",
                    "status": "error"
                }
            }
        return {
            "response": {
                "id": "4915862683607007234",
                "phone": f"91{mobile_number}",
                "details": "OTP matched.",
                "status": "success"
            }
        }
