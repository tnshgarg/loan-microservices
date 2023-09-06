from dal.models.employees import Employee
from fastapi import HTTPResponseException
from services.otp.gupshup.gupshup_otp_service import GupshupOtpService
from services.otp.mobile_verification_service import MobileVerificationService
from services.otp.payloads import MobileGenerateOtpPayload, MobileVerifyOtpPayload
from services.otp.route_mobile.route_mobile_otp_service import RouteMobileOtpService
from services.otp.sales_user.sales_user_otp_service import SalesUserVerificationService

MOCK_PHONES = [str(i) * 10 for i in range(1, 10)]


class OTPController(Controller):

    def _get_otp_service(self) -> MobileVerificationService:
        provider = self.event["body-json"].get("provider", "routemobile")
        phone = self.event["body-json"].get("mobileNumber")
        if provider is None or provider not in ('gupshup', 'routemobile', 'rmpin'):
            raise HTTPResponseException(
                status_code=400,
                message="`provider` not supported"
            )
        use_mock = phone in MOCK_PHONES
        if provider == "gupshup":
            return GupshupOtpService(self.logger, self.stage, use_mock)
        elif provider == "rmpin":
            return SalesUserVerificationService(self.logger, self.stage, use_mock)
        else:
            return RouteMobileOtpService(self.logger, self.stage, use_mock)

    def _store_version_header(self, mobile_number):
        version_header = self.event.get(
            "params", {}).get("header", {}).get("x-unipe-app-version")
        Employee.update_one({
            "mobile": mobile_number[-10:]
        }, {
            "$set": {
                "context.last_login_version": version_header
            }
        }, upsert=False)

    def _handle_post(self, category: str):
        self.logger.info("OTPController ", extra={
            "data": {"msg": "_handle_post"}
        })
        if category == "generate-otp":
            return self._handle_generate_otp()
        elif category == "verify-otp":
            return self._handle_verify_otp()

    def _handle_generate_otp(self):
        payload = self._parse_body(MobileGenerateOtpPayload)
        otp_service = self._get_otp_service()
        return otp_service.generate_otp(payload)

    def _handle_verify_otp(self):
        constants = Constants(self.event)
        payload = self._parse_body(MobileVerifyOtpPayload)
        self._store_version_header(payload.mobile_number)
        otp_service = self._get_otp_service()
        return otp_service.verify_otp(payload, constants.jwt_secret)
