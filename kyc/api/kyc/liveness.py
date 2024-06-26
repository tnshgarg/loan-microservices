from typing import Annotated
from fastapi import APIRouter, File, HTTPException, UploadFile, Depends, status
from kyc.dependencies.auth import get_sales_current_session
from kyc.dependencies.kyc import gdrive_upload_service, loans_gdrive_upload_service, s3_upload_service, google_sheets_service
from kyc.schemas.auth import TokenPayload
from services.kyc.liveness_service import LivenessService
from services.storage.sheets.google_sheets import GoogleSheetsService
from services.storage.uploads.drive_upload_service import DriveUploadService
from services.storage.uploads.s3_upload_service import S3UploadService

router = APIRouter()


@router.post("/profile-pic")
async def upload_profile_pic(
    profile_pic: Annotated[UploadFile, File()],
    gdrive_upload_service: Annotated[DriveUploadService, Depends(loans_gdrive_upload_service)],
    s3_upload_service: Annotated[S3UploadService, Depends(s3_upload_service)],
    google_sheets_service: Annotated[GoogleSheetsService, Depends(google_sheets_service)],
    user: Annotated[TokenPayload, Depends(get_sales_current_session)]
):
    liveness_service = LivenessService(
        user.unipe_employee_id,
        user.sales_user_id,
        gdrive_upload_service,
        s3_upload_service,
        google_sheets_service
    )

    liveness_check_result = liveness_service.perform_liveness_check(
        profile_pic)

    if liveness_check_result == "SUCCESS":
        return {"status": 200, "message": "Liveness check successful"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=liveness_check_result
        )
