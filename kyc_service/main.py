from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from dal.models.db_manager import DBManager
from dal.models.employees import Employee
from dal.models.sales_users import SalesUser
from .auth import create_access_token, create_refresh_token, valid_client
from .config import Config
from .schemas.auth import TokenSchema
from .api.kyc.aadhaar_ocr import router as aadhaar_ocr_router
from .api.otp.login_otp import router as login_otp_router
from .api.ewa.video_otp import router as video_otp_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


origins = [
    "http://localhost:3000",
    "https://qa.d2ofz3ql5xiuyy.amplifyapp.com",
    "https://dev.d2ofz3ql5xiuyy.amplifyapp.com",
    "https://sales-webapp.unipe.money"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def start_db():
    DBManager.init(Config.STAGE)


@app.get("/ping")
async def ping():
    return {"status": 200, "stage": Config.STAGE}

app.include_router(
    aadhaar_ocr_router,
    prefix="/{stage}/kyc-service"
)
app.include_router(
    video_otp_router,
    prefix="/{stage}/kyc-service"
)
app.include_router(
    login_otp_router,
    prefix="/{stage}/otp-service"
)


@app.post('/{stage}/kyc-service/token', summary="Create access and refresh tokens for sales_users", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not valid_client(form_data.client_id, form_data.client_secret):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Client"
        )

    sales_user = SalesUser.find_one({"hashed_pw": form_data.password})
    employee = Employee.find_one({"mobile": form_data.username})
    if employee is None or sales_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can't Locate User"
        )

    return {
        "access_token": create_access_token(
            unipe_employee_id=str(employee["_id"]),
            sales_user_id=str(sales_user["_id"]),
            client_id=form_data.client_id
        ),
        "refresh_token": create_refresh_token(
            unipe_employee_id=str(employee["_id"]),
            sales_user_id=str(sales_user["_id"]),
            client_id=form_data.client_id
        ),
    }
