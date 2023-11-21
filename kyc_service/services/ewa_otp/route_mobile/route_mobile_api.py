import json
import os
import requests

GENERATE_OTP_MAP = {
    "1701": "Success, Message submitted successfully.",
    "1702": "One of the parameter is missing or OTP is not numeric.",
    "1703": "User authentication has failed.",
    "1705": "Message does not contain \"%m\".",
    "1706": "Invalid destination.",
    "1707": "Invalid Sender ID.",
    "1710": "Internal error.",
    "1715": "Response time out.",
    "1025": "Insufficient user credit.",
    "1032": "DND destination.",
    "1033": "Source template mismatch.",
    "1035": "User has unsubscribed.",
    "1042": "Explicit DND reject.",
}
VERIFY_OTP_MAP = {
    "101": "Success, OTP validated successfully.",
    "102": "OTP has expired.",
    "103": "Entry for OTP not found.",
    "104": "MSISDN not found.",
    "1702": "One of the parameter is missing or OTP is not numeric.",
    "1703": "Authentication has failed.",
    "1706": "Given destination is invalid.",
}

SUCCESS_CODES = ("1701", "101")


class RouteMobileApi:

    def __init__(self, logger) -> None:
        self.logger = logger

        self.route_mobile_assets = json.loads(
            os.environ.get("route_mobile_secret", "{}"))
        self.base_url = self.route_mobile_assets.get("base_url")
        # print("baseurl: ", self.base_url)
        self.route_mobile_userid = self.route_mobile_assets.get("userid")
        self.route_mobile_password = self.route_mobile_assets.get("password")
        self.otp_string = self.route_mobile_assets.get("otp_message_string")

    def merge_url(self, val):
        return val[0] + "=" + val[1]

    def build_querystring(self, params):
        return "&".join(list(map(self.merge_url, params.items())))

    def parse_response_string(self, response_text, request_type="generate"):
        status_code_map = GENERATE_OTP_MAP if request_type == "generate" else VERIFY_OTP_MAP
        code = response_text.split("|")[0]
        message = status_code_map[code]
        return {
            "response": {
                "code": code,
                "details": message,
                "status": "success" if code in SUCCESS_CODES else "error"
            }
        }

    def generate_otp(self, mobile_number: str):
        try:
            params = {
                "username": self.route_mobile_userid,
                "password": self.route_mobile_password,
                "msisdn": mobile_number,
                "tempid": self.route_mobile_assets.get('tempid'),
                "entityid": self.route_mobile_assets.get('entityid'),
                "exptime": "3600",
                "msg": self.otp_string,
                "otplen": "6",
                "source": "PYRCKT"
            }

            query = "/otpgenerate?" + self.build_querystring(params)

            url = self.base_url+query
            self.logger.info("mobile_generate_otp_url", extra={
                "data": {"url": url}
            })

            response = requests.get(
                url=url
            )
            response_text = response.text

            self.logger.info("mobile_generate_otp_res", extra={
                "data": {"text": response_text}
            })

            response = self.parse_response_string(
                response_text, request_type="generate")
            return response
        except Exception as e:
            print("Exception: ", e)
            self.logger.info("mobile_generate_otp_res", extra={
                "error": e,
                "status": 400
            })

    def verify_otp(self, mobile_number: str, otp: str):
        try:
            params = {
                "username": self.route_mobile_userid,
                "password": self.route_mobile_password,
                "msisdn": mobile_number,
                "otp": otp
            }
            query = "/checkotp?" + self.build_querystring(params)
            url = self.base_url+query
            self.logger.info("verify_otp_url", extra={
                "data": {"url": url}
            })
            response = requests.get(url=url)
            response_text = response.text
            self.logger.info("verify_otp_res", extra={
                "data": {"text": response_text}
            })
            response = self.parse_response_string(
                response_text, request_type="verify")
            response["response"]["phone"] = mobile_number
            return response
        except Exception as e:
            print(e)
            self.logger.info("mobile_verify_otp_res", extra={
                "error": e,
                "status": 400
            })
