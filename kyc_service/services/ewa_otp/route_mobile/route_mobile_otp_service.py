from fastapi import HTTPException as HTTPResponseException
from kyc_service.services.ewa_otp.mobile_verification_service import MobileVerificationService
from .route_mobile_api import RouteMobileApi
from .route_mobile_api_mock import RouteMobileApiMock
from dal.models.offer import Offers
from dal.models.ewa_otp import EwaOTP
from kyc_service.services.storage.uploads.drive_upload_service import DriveUploadService
from dal.utils import db_txn

class RouteMobileOtpService(MobileVerificationService):

    def __init__(self, logger, stage, use_mock=False) -> None:
        super().__init__()
        self.logger = logger
        self.stage = stage
        self.gdrive_upload_service = DriveUploadService(logger)
        if use_mock:
            self.route_mobile_api = RouteMobileApiMock(logger)
        else:
            self.route_mobile_api = RouteMobileApi(logger)
    @db_txn
    def generate_otp(self, payload, user):
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
                EwaOTP.update(
                {
                    "unipeEmployeeId": user.unipe_employee_id,
                    "status": EwaOTP.Stage.PENDING
                },
                {
                    "$set": {
                        "status": EwaOTP.Stage.EXPIRED
                    }
                }
                )
                EwaOTP.insert_one({
                    "unipeEmployeeId": user.unipe_employee_id,
                    "status": EwaOTP.Stage.PENDING,
                    "offerId": payload.offer_id,
                })
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
    
    @db_txn
    def verify_otp(self, payload, user):
        try:
            mobile_verify_otp_response_raw = self.route_mobile_api.verify_otp(
                mobile_number=payload.mobile_number,
                otp=payload.otp,
            )
            mobile_verify_otp_response = mobile_verify_otp_response_raw.get(
                "response")
            if mobile_verify_otp_response.get("status") == "success":
                mobile_verify_otp_response["status"] = 200

                EwaOTP.update_one({
                    "unipeEmployeeId": user.unipe_employee_id,
                    "status": EwaOTP.Stage.PENDING,
                    "offerId": payload.offer_id,
                }, {"$set": {
                    "status": EwaOTP.Stage.SUBMITTED,
                }})
                # Offers.update_one({
                #     "_id": user["offer_id"],
                # }, {"$set": {
                #     "kycFolder": self.gdrive_upload_service.get_employee_root_url(str(user.unipe_employee_id))
                # }})
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
