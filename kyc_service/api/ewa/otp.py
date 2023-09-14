from typing import Annotated
from fastapi import APIRouter, Header, Form, Depends
from kyc_service.services.ewa_otp.ewa_otp_service import EwaOtpService
from kyc_service.schemas.auth import GenerateOtpPayload, VerifyOtpPayload
from kyc_service.dependencies.auth import get_current_session
from kyc_service.schemas.auth import TokenPayload
import bson

router = APIRouter()


@router.post("/generate-otp/")
async def generate_otp(otp_payload: GenerateOtpPayload):
    user={"unipe_employee_id" : bson.ObjectId("bbbbbbbbbbbbbbbbbbbbbbbb")}
    ewa_service = EwaOtpService()._handle_generate_otp(otp_payload, user)
    return ewa_service


@router.post("/verify-otp/")
async def generate_otp(otp_payload: VerifyOtpPayload):
    user={"unipe_employee_id" : bson.ObjectId("bbbbbbbbbbbbbbbbbbbbbbbb")}
    ewa_service = EwaOtpService()
    verify_otp_response = ewa_service._handle_verify_otp(otp_payload, user)
    return verify_otp_response
