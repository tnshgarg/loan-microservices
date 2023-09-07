from typing import Annotated
from fastapi import APIRouter, File, Form, UploadFile, Depends
import base64
import requests
from kyc_service.dependencies.auth import get_current_session
from kyc_service.schemas.auth import TokenPayload
from kyc_service.services.otp.login_otp_service import LoginOtpService


router = APIRouter()


@router.get("/aadhaar")
async def get_aadhaar():
    return {"foo": "bar"}


@router.post("/generate-otp")
async def generate_otp(
    front_image: Annotated[UploadFile, File()],
    back_image: Annotated[UploadFile, File()],
    signature: Annotated[UploadFile, File()],
    gridlines_api: Annotated[GridlinesApi, Depends(gridlines_api)],
    gdrive_upload_service: Annotated[DriveUploadService, Depends(gdrive_upload_service)],
    s3_upload_service: Annotated[DriveUploadService, Depends(s3_upload_service)],
    google_sheets_service: Annotated[GoogleSheetsService, Depends(google_sheets_service)],
    user: Annotated[TokenPayload, Depends(get_current_session)]
):
    login_service = LoginOtpService()
    login_service._handle_generate_otp()

    return {"foo": "bar"}


