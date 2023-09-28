import json
import os
import requests


class GupshupApi:

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
        try:
            self.params = {
                "userid": self.gupshup_userid,
                "password": self.gupshup_password,
                "method": "TWO_FACTOR_AUTH",
                "v": "1.1",
                "phone_no": mobile_number,
                "msg": self.otp_string,
                "format": "JSON",
                "otpCodeLength": "6",
                "otpCodeType": "NUMERIC"
            }
            query = "&".join(list(map(self.merge_url, self.params.keys())))
            url = self.base_url+query
            self.logger.info("mobile_generate_otp_url", extra={
                "data": {"url": url}
            })

            response = requests.post(
                url=url,
                headers=self.headers
            )
            response_json = response.json()

            self.logger.info("mobile_generate_otp_res", extra={
                "data": response_json
            })
            return response_json
        except Exception as e:
            print("Exception: ", e)
            self.logger.info("mobile_generate_otp_res", extra={
                "error": e,
                "status": 400
            })

    def verify_otp(self, mobile_number: str, otp: str):
        try:
            self.params = {
                "userid": self.gupshup_userid,
                "password": self.gupshup_password,
                "method": "TWO_FACTOR_AUTH",
                "v": "1.1",
                "phone_no": mobile_number,
                "format": "JSON",
                "otp_code": otp,
            }
            query = "&".join(list(map(self.merge_url, self.params.keys())))
            url = self.base_url+query
            self.logger.info("verify_otp_url", extra={
                "data": {"url": url}
            })
            response = requests.post(
                url=url,
                headers=self.headers,
                json=self.params
            )
            response_json = response.json()
            self.logger.info("verify_otp_res", extra={
                "data": response_json
            })
            return response_json
        except Exception as e:
            print(e)
            self.logger.info("mobile_generate_otp_res", extra={
                "error": e,
                "status": 400
            })
