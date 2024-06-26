import bson
from fastapi import APIRouter, File, Form, UploadFile, Depends
from typing import Annotated
from kyc.dependencies.auth import get_sales_current_session
from kyc.dependencies.kyc import gdrive_upload_service, google_sheets_service, s3_upload_service

from kyc.schemas.auth import SalesTokenPayload
from services.ewa.otp.video.ewa_video_otp_service import VideoOtpService
from services.storage.sheets.google_sheets import GoogleSheetsService
from services.storage.uploads.drive_upload_service import DriveUploadService
from services.storage.uploads.s3_upload_service import S3UploadService

router = APIRouter()


@router.post("/generate-ewa-otp")
async def generate_ewa_otp(
    offer_id: Annotated[str, Form()],
    user: Annotated[SalesTokenPayload, Depends(get_sales_current_session)]
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
    user: Annotated[SalesTokenPayload, Depends(get_sales_current_session)]
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
