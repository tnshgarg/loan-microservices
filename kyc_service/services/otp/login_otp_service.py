import os 
from dal.models.employees import Employee
from kyc_service.config import Config
from fastapi import HTTPException as HTTPResponseException
from .gupshup.gupshup_otp_service import GupshupOtpService
from .mobile_verification_service import MobileVerificationService
from .payloads import MobileGenerateOtpPayload, MobileVerifyOtpPayload
from .route_mobile.route_mobile_otp_service import RouteMobileOtpService
from .sales_user.sales_user_otp_service import SalesUserVerificationService
from dal.logger import get_app_logger

MOCK_PHONES = [str(i) * 10 for i in range(1, 10)]


class LoginOtpService():

    def __init__(self):
        self.stage = os.environ["STAGE"]
        self.logger = get_app_logger("ops-microservice", self.stage)
        self.ops_microservice_url = os.environ["OPS_MICROSERVICE_URL"]

    def _get_otp_service(self, payload) -> MobileVerificationService:
        if payload.provider is None or payload.provider not in ('gupshup', 'routemobile', 'rmpin'):
            raise HTTPResponseException(
                status_code=400,
                detail="`provider` not supported"
            )
        use_mock = payload.mobile_number in MOCK_PHONES
        if payload.provider == "gupshup":
            return GupshupOtpService(self.logger, Config.STAGE, use_mock)
        elif payload.provider == "rmpin":
            return SalesUserVerificationService(self.logger, Config.STAGE, use_mock)
        else:
            return RouteMobileOtpService(self.logger, Config.STAGE, use_mock)

    def _store_version_header(self, app_version, mobile_number):
        Employee.update_one({
            "mobile": mobile_number[-10:]
        }, {
            "$set": {
                "context.last_login_version": app_version
            }
        }, upsert=False)

    def _handle_generate_otp(self, payload):
        otp_service = self._get_otp_service(payload)
        return otp_service.generate_otp(payload)

    def _handle_verify_otp(self, payload, app_version):
        jwt_secret = os.environ["jwt_secret"]
        self._store_version_header(app_version, payload.mobile_number)
        otp_service = self._get_otp_service(payload)
        return otp_service.verify_otp(payload, jwt_secret)
