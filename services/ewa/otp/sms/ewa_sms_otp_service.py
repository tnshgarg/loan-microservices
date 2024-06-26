import os
from dal.models.employees import Employee
from kyc.config import Config
from fastapi import HTTPException as HTTPResponseException
from .gupshup.gupshup_otp_service import GupshupOtpService
from .mobile_verification_service import MobileVerificationService
from .route_mobile.route_mobile_otp_service import RouteMobileOtpService
from dal.logger import get_app_logger
from kyc.dependencies.kyc import gdrive_upload_service, google_sheets_service, s3_upload_service

MOCK_PHONES = [str(i) * 10 for i in range(1, 10)]


class EwaOtpService:

    def __init__(self):
        self.logger = get_app_logger(
            app_name="ewa-otp-service", stage=Config.STAGE)

    def _get_otp_service(self, payload, user) -> MobileVerificationService:
        if payload.provider is None or payload.provider not in ('gupshup', 'routemobile'):
            raise HTTPResponseException(
                status_code=400,
                detail="`provider` not supported"
            )
        use_mock = payload.mobile_number in MOCK_PHONES
        if payload.provider == "gupshup":
            return GupshupOtpService(self.logger, Config.STAGE, use_mock)
        else:
            return RouteMobileOtpService(self.logger, Config.STAGE, unipe_employee_id=user.unipe_employee_id, sales_user_id=None,  gdrive_upload_service=gdrive_upload_service,
                                         s3_upload_service=s3_upload_service,
                                         google_sheets_service=google_sheets_service, use_mock=use_mock)

    def _handle_generate_otp(self, payload, user):
        otp_service = self._get_otp_service(payload, user)
        return otp_service.generate_otp(payload, user)

    def _handle_verify_otp(self, payload, user):
        otp_service = self._get_otp_service(payload, user)
        return otp_service.verify_otp(payload, user)
