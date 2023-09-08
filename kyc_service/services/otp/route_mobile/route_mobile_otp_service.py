from fastapi import HTTPException as HTTPResponseException
from kyc_service.services.otp.mobile_verification_service import MobileVerificationService
from .route_mobile_api import RouteMobileApi
from .route_mobile_api_mock import RouteMobileApiMock


class RouteMobileOtpService(MobileVerificationService):

    def __init__(self, logger, stage, use_mock=False) -> None:
        super().__init__()
        self.logger = logger
        self.stage = stage

        if use_mock:
            self.route_mobile_api = RouteMobileApiMock(logger)
        else:
            self.route_mobile_api = RouteMobileApi(logger)

    def generate_otp(self, payload):
        try:
            if not self.is_mobile_registered(payload.mobile_number):
                return {
                    "status": 404,
                    "code": "MOBILE_NOT_REGISTERED",
                    "message": "Mobile Number not Registered with Unipe please check number or contact employer"
                }
            mobile_generate_otp_response = self.route_mobile_api.generate_otp(
                mobile_number=payload.mobile_number,
            )
            self.logger.info("mobile_generate_otp_res", extra={
                "data": mobile_generate_otp_response
            })

            if mobile_generate_otp_response["response"]["status"] == "success":
                mobile_generate_otp_response["status"] = 200
            else:
                raise Exception("Some Problem generating error")

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
        try:
            mobile_verify_otp_response_raw = self.route_mobile_api.verify_otp(
                mobile_number=payload.mobile_number,
                otp=payload.otp,
            )
            mobile_verify_otp_response = mobile_verify_otp_response_raw.get(
                "response")
            if mobile_verify_otp_response.get("status") == "success":
                token, employee_details = self.generate_jwt_token(
                    mobile_verify_otp_response["phone"][-10:], secret)
                if token is None:
                    raise HTTPResponseException(
                        status_code=404,
                        detail="Mobile Number not found"
                    )

                mobile_verify_otp_response["token"] = token
                mobile_verify_otp_response["employeeDetails"] = employee_details
                mobile_verify_otp_response["status"] = 200
            elif mobile_verify_otp_response["code"] == "103":
                mobile_verify_otp_response["status"] = 406
            else:
                mobile_verify_otp_response["status"] = 400
            self.logger.info("mobile_verify_otp_res", extra={
                "data": mobile_verify_otp_response
            })
            return mobile_verify_otp_response
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
