
from fastapi import HTTPException as HTTPResponseException
from services.ewa.otp.sms.mobile_verification_service import MobileVerificationService
from .gupshup_api import GupshupApi
from .gupshup_api_mock import GupshupApiMock


class GupshupOtpService(MobileVerificationService):

    def __init__(self, logger, stage, use_mock=False) -> None:
        super().__init__()
        self.logger = logger
        self.stage = stage

        if use_mock:
            self.gupshup_api = GupshupApiMock(logger, "dev")
        else:
            self.gupshup_api = GupshupApi(logger)

    def generate_otp(self, payload):
        if payload.mobile_number in ["7" * 10, "8" * 10, "8" * 10]:
            self.gupshup_api = GupshupApiMock(self.logger)
        try:
            if not self.is_mobile_registered(payload.mobile_number):
                return {
                    "status": 404,
                    "code": "MOBILE_NOT_REGISTERED",
                    "message": "Mobile Number not Registered with Unipe please check number or contact employer"
                }
            mobile_generate_otp_response = self.gupshup_api.generate_otp(
                mobile_number=payload.mobile_number,
            )
            self.logger.info("mobile_generate_otp_res", extra={
                "data": mobile_generate_otp_response
            })
            return mobile_generate_otp_response
        except Exception as e:
            self.logger.info("mobile_generate_otp_res", extra={
                "data": {
                    "status": 400,
                    "error": str(e)
                }
            })
            raise HTTPResponseException(
                status_code=400,
                detail=str(e)
            )

    def verify_otp(self, payload, secret):
        if payload.mobile_number in ["7" * 10, "8" * 10, "8" * 10]:
            self.gupshup_api = GupshupApiMock(self.logger)
        try:
            mobile_verify_otp_response = self.gupshup_api.verify_otp(
                mobile_number=payload.mobile_number,
                otp=payload.otp,
            )
            response_status = mobile_verify_otp_response.get(
                "response", {}).get("status")
            response_body_code = mobile_verify_otp_response.get(
                "body", {}).get("code")

            if response_status == "success":
                token, employee_details = self.generate_jwt_token(
                    mobile_verify_otp_response["response"]["phone"][-10:], secret)
                if token is None:
                    raise HTTPResponseException(
                        status_code=404,
                        detail="Mobile Number not found"
                    )

                mobile_verify_otp_response["response"]["token"] = token
                mobile_verify_otp_response["response"]["employeeDetails"] = employee_details
                mobile_verify_otp_response["response"]["status"] = 200
            elif response_body_code == "INVALID_OTP":
                mobile_verify_otp_response["response"]["status"] = 406
            elif response_status != "success":
                mobile_verify_otp_response["response"]["status"] = 408
            else:
                mobile_verify_otp_response["response"]["status"] = 400

            self.logger.info("mobile_verify_otp_res", extra={
                "data": mobile_verify_otp_response
            })

            return mobile_verify_otp_response.get("response", {})
        except Exception as e:
            self.logger.info("mobile_generate_otp_res", extra={
                "data": {
                    "status": 400,
                    "error": str(e)
                }
            })
            raise HTTPResponseException(
                status_code=400,
                detail=str(e)
            )
