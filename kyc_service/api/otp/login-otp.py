from typing import Annotated
from fastapi import APIRouter, File, Form, UploadFile, Depends
import base64
import requests
from kyc_service.dependencies.auth import get_current_session
from kyc_service.dependencies.kyc import gdrive_upload_service, google_sheets_service, gridlines_api, s3_upload_service
from kyc_service.schemas.auth import TokenPayload

from kyc_service.services.kyc.gridlines import GridlinesApi
from kyc_service.services.kyc.kyc_ocr_service import KYCOCRService
from kyc_service.services.storage.sheets.google_sheets import GoogleSheetsService
from kyc_service.services.storage.uploads.drive_upload_service import DriveUploadService
from kyc_service.services.storage.uploads.s3_upload_service import S3UploadService

router = APIRouter()


@router.get("/aadhaar")
async def get_aadhaar():
    return {"foo": "bar"}


@router.post("/aadhaar")
async def upload_aadhaar(
    front_image: Annotated[UploadFile, File()],
    back_image: Annotated[UploadFile, File()],
    signature: Annotated[UploadFile, File()],
    gridlines_api: Annotated[GridlinesApi, Depends(gridlines_api)],
    gdrive_upload_service: Annotated[DriveUploadService, Depends(gdrive_upload_service)],
    s3_upload_service: Annotated[DriveUploadService, Depends(s3_upload_service)],
    google_sheets_service: Annotated[GoogleSheetsService, Depends(google_sheets_service)],
    user: Annotated[TokenPayload, Depends(get_current_session)]
):
    kyc_service = KYCOCRService(
        user.unipe_employee_id,
        user.sales_user_id,
        gridlines_api,
        gdrive_upload_service,
        s3_upload_service,
        google_sheets_service
    )
    kyc_service.perform_aadhaar_kyc(front_image, back_image, signature)

    return {"foo": "bar"}


@router.post("/user-photos")
async def upload_user_photos(user_photo: Annotated[UploadFile, File()],
                             user_idphoto: Annotated[UploadFile, File()],
                             gridlines_api: Annotated[GridlinesApi, Depends(gridlines_api)],
                             gdrive_upload_service: Annotated[DriveUploadService, Depends(gdrive_upload_service)],
                             s3_upload_service: Annotated[S3UploadService, Depends(s3_upload_service)],
                             google_sheets_service: Annotated[GoogleSheetsService, Depends(google_sheets_service)],
                             user: Annotated[TokenPayload, Depends(get_current_session)]):
    kyc_service = KYCOCRService(
        user.unipe_employee_id,
        user.sales_user_id,
        gridlines_api,
        gdrive_upload_service,
        s3_upload_service,
        google_sheets_service
    )
    kyc_service.perform_user_verification(user_photo, user_idphoto)

    return {"foo": "bar"}
