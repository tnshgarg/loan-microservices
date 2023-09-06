import json
import os
import requests
from exceptions import HTTPResponseException
from services.otp.mobile_verification_service import MobileVerificationService
from config import UnipeConfig


class SalesUserVerificationService(MobileVerificationService):

    def __init__(self, logger, stage, use_mock=False) -> None:
        super().__init__()
        if UnipeConfig.ASSET != UnipeConfig.SALES_APP_ASSET:
            raise HTTPResponseException(
                status_code=404,
                message="User Not Found"
            )

        self.logger = logger
        self.stage = stage
        kyc_service_credentials = json.loads(os.getenv("kyc_service_creds"))
        self.kyc_service_url = kyc_service_credentials["base_url"]
        self.client_id = kyc_service_credentials["client_id"]
        self.client_secret = kyc_service_credentials["client_secret"]

    def generate_otp(self, payload):
        try:
            if not self.is_mobile_registered(payload.mobile_number):
                return {
                    "status": 404,
                    "code": "MOBILE_NOT_REGISTERED",
                    "message": "Mobile Number not Registered with Unipe please check number or contact employer"
                }

            return {
                "status": 200,
                "code": "MOBILE_FOUND",
                "message": "User Verified, Number Exists"
            }
        except Exception as e:
            self.logger.info("mobile_generate_otp_res", extra={
                "data": {
                    "status": 400,
                    "error": str(e)
                }
            })
            raise HTTPResponseException(
                status_code=400,
                message=str(e)
            )

    def verify_otp(self, payload, secret):
        try:
            response = requests.post(
                url=self.kyc_service_url + "/token",
                data={
                    "username": payload.mobile_number,
                    "password": payload.otp,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                }
            )
            kyc_service_token_response = response.json()
            self.logger.info("mobile_verify_otp_res", extra={
                "data": kyc_service_token_response
            })
            if response.status_code == 200:
                token, employee_details = self.generate_jwt_token(
                    payload.mobile_number[-10:], secret)
                if token is None:
                    raise HTTPResponseException(
                        status_code=404,
                        message="Mobile Number not found"
                    )

                return {
                    "status": 200,
                    "token": token,
                    "kyc_service_tokens": kyc_service_token_response,
                    "employeeDetails": employee_details
                }
            else:
                return {
                    "status": 400,
                    "message": kyc_service_token_response.get("details", "Unable to Authenticate")
                }

        except Exception as e:
            self.logger.info("mobile_generate_otp_res", extra={
                "data": {
                    "status": 400,
                    "error": str(e)
                }
            })
            raise HTTPResponseException(
                status_code=400,
                message=str(e)
            )
