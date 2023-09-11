from typing import Annotated
from fastapi import APIRouter, Header
from kyc_service.services.otp.login_otp_service import LoginOtpService
from kyc_service.schemas.auth import GenerateOtpPayload, VerifyOtpPayload

router = APIRouter()


@router.get("/")
async def get_aadhaar():
    return {"foo": "bar"}


@router.post("/generate-otp/")
async def generate_otp(otp_payload: GenerateOtpPayload):
    login_service = LoginOtpService()
    generate_otp_response = login_service._handle_generate_otp(otp_payload)
    return generate_otp_response


@router.post("/verify-otp/")
async def generate_otp(otp_payload: VerifyOtpPayload,  x_unipe_app_version: Annotated[str | None, Header(convert_underscores=True)] = None):
    login_service = LoginOtpService()
    verify_otp_response = login_service._handle_verify_otp(otp_payload , x_unipe_app_version)
    return verify_otp_response


