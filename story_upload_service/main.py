from typing import Annotated
from fastapi import APIRouter, FastAPI, Depends, HTTPException, UploadFile, File,  status

from dal.models.db_manager import DBManager
from dal.models.employees import Employee
from services.storage.uploads.drive_upload_service import DriveUploadService
from kyc.schemas.auth import TokenPayload
from kyc.dependencies.auth import get_current_session
from story_upload_service.auth import UserUploadSchema
from services.user_story.story_upload_service import StoryUploadService
from kyc.config import Config
from fastapi.middleware.cors import CORSMiddleware
from kyc.dependencies.kyc import gdrive_upload_service

user_story_router = APIRouter()


@user_story_router.post('/{stage}/story-upload-service', summary="Upload user story to backend", response_model=UserUploadSchema)
async def upload_story(user_story: Annotated[UploadFile, File()],  gdrive_upload_service: Annotated[DriveUploadService, Depends(gdrive_upload_service)], user: Annotated[TokenPayload, Depends(get_current_session)]):
    media_upload_service = StoryUploadService(
        user_story,
        unipe_employee_id=user.unipe_employee_id,
        gdrive_upload_service=gdrive_upload_service,
    )
    uploaded_video = media_upload_service.upload_user_story(user_story)

    employee = Employee.find_one({"_id": user.unipe_employee_id})

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can't Locate User"
        )

    if uploaded_video is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can't Upload the User Story"
        )

    return {
        "status": status.HTTP_200_OK,
        "video": uploaded_video
    }
