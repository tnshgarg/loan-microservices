from fastapi import APIRouter, File, Form, UploadFile, Depends
from typing import Annotated
from kyc_service.dependencies.auth import get_current_session

from kyc_service.schemas.auth import TokenPayload

router = APIRouter()


@router.post("/generate-ewa-otp")
async def get_aadhaar(
    offer_id: Annotated[str, Form()],
    user: Annotated[TokenPayload, Depends(get_current_session)]
):
    return {"foo": "bar"}


@router.post("/verify-ewa-otp")
async def upload_aadhaar(
    offer_id: Annotated[str, Form()],
    front_image: Annotated[UploadFile, File()],
    user: Annotated[TokenPayload, Depends(get_current_session)]
):
    return {"foo": "bar"}
