import os 
from dal.models.employees import Employee
from kyc_service.config import Config
from fastapi import HTTPException as HTTPResponseException
from .gupshup.gupshup_otp_service import GupshupOtpService
from .mobile_verification_service import MobileVerificationService
from .route_mobile.route_mobile_otp_service import RouteMobileOtpService
from dal.logger import get_app_logger

MOCK_PHONES = [str(i) * 10 for i in range(1, 10)]


class EwaOtpService():

    def __init__(self):
        self.stage = os.environ["STAGE"]
        self.logger = get_app_logger("ops-microservice", self.stage)
        self.ops_microservice_url = os.environ["OPS_MICROSERVICE_URL"]

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
            return RouteMobileOtpService(self.logger, Config.STAGE, use_mock)

    def _handle_generate_otp(self, payload, user):
        otp_service = self._get_otp_service(payload, user)
        return otp_service.generate_otp(payload, user)

    def _handle_verify_otp(self, payload, user):
        otp_service = self._get_otp_service(payload, user)
        return otp_service.verify_otp(payload, user)
