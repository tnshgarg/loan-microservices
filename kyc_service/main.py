from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from dal.models.db_manager import DBManager
from dal.models.employees import Employee
from dal.models.sales_users import SalesUser
from .auth import create_access_token, create_refresh_token, valid_client
from .config import Config
from .schemas.auth import TokenSchema
from .api.kyc.aadhaar_ocr import router as aadhaar_ocr_router
from .api.ewa.otp import router as ewa_otp_router
from .api.ewa.video_otp import router as video_otp_router
from .api.kyc.liveness import router as liveness_router
from .api.kyc.token import token_router
from .api.utils.pincode_details import router as pincode_details_router
from .api.ewa.ewa import ewa_router
from .api.kyc.token import token_router

app = FastAPI()


app.include_router(
    aadhaar_ocr_router,
    prefix="/{stage}/kyc-service"
)
app.include_router(
    liveness_router,
    prefix="/{stage}/kyc-service"
)

app.include_router(
    token_router,
    prefix="/{stage}/kyc-service"
)

app.include_router(
    video_otp_router,
    prefix="/{stage}/video-service"
)

app.include_router(
    ewa_otp_router,
    prefix="/{stage}/otp-service"
)

app.include_router(
    pincode_details_router,
    prefix="/{stage}/utility-service"
)

app.include_router(
    ewa_router,
    prefix="/{stage}/ewa-service"
)

app.include_router(
    token_router,
    prefix="/{stage}/kyc-service"
)
