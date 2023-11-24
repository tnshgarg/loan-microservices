from typing import Annotated
from fastapi import APIRouter, Depends
from services.ewa.otp.sms.ewa_sms_otp_service import EwaOtpService
from kyc.schemas.auth import GenerateOtpPayload, VerifyOtpPayload
from kyc.dependencies.auth import get_current_session
from kyc.schemas.auth import TokenPayload
import bson

router = APIRouter()


@router.post("/generate-otp")
async def generate_otp(otp_payload: GenerateOtpPayload, user: Annotated[TokenPayload, Depends(get_current_session)]):
    ewa_service = EwaOtpService()._handle_generate_otp(otp_payload, user)
    return ewa_service


@router.post("/verify-otp")
async def generate_otp(otp_payload: VerifyOtpPayload, user: Annotated[TokenPayload, Depends(get_current_session)]):
    ewa_service = EwaOtpService()
    verify_otp_response = ewa_service._handle_verify_otp(otp_payload, user)
    return verify_otp_response
