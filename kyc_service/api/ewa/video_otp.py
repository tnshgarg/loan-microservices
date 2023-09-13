import bson
from fastapi import APIRouter, File, Form, UploadFile, Depends
from typing import Annotated
from kyc_service.dependencies.auth import get_current_session
from kyc_service.dependencies.kyc import gdrive_upload_service, google_sheets_service, s3_upload_service

from kyc_service.schemas.auth import TokenPayload
from kyc_service.services.ewa_video_otp.ewa_otp_service import VideoOtpService
from kyc_service.services.storage.sheets.google_sheets import GoogleSheetsService
from kyc_service.services.storage.uploads.drive_upload_service import DriveUploadService
from kyc_service.services.storage.uploads.s3_upload_service import S3UploadService

router = APIRouter()


@router.post("/generate-ewa-otp")
async def generate_ewa_otp(
    offer_id: Annotated[str, Form()],
    user: Annotated[TokenPayload, Depends(get_current_session)]
):
    generated_otp = VideoOtpService(
        unipe_employee_id=user.unipe_employee_id,
        sales_user_id=user.sales_user_id,
        gdrive_upload_service=None,
        s3_upload_service=None,
        google_sheets_service=None
    ).generate_otp(bson.ObjectId(offer_id))
    return {"otp": generated_otp}


@router.post("/verify-ewa-otp")
async def verify_ewa_otp(
    offer_id: Annotated[str, Form()],
    video_otp: Annotated[UploadFile, File()],
    gdrive_upload_service: Annotated[DriveUploadService, Depends(gdrive_upload_service)],
    s3_upload_service: Annotated[S3UploadService, Depends(s3_upload_service)],
    google_sheets_service: Annotated[GoogleSheetsService, Depends(google_sheets_service)],
    user: Annotated[TokenPayload, Depends(get_current_session)]
):
    VideoOtpService(
        unipe_employee_id=user.unipe_employee_id,
        sales_user_id=user.sales_user_id,
        gdrive_upload_service=gdrive_upload_service,
        s3_upload_service=s3_upload_service,
        google_sheets_service=google_sheets_service
    ).verify_otp(
        uploaded_video=video_otp,
        offer_id=bson.ObjectId(offer_id),
        sales_user_id=user.sales_user_id
    )
    return {"success": "true"}
