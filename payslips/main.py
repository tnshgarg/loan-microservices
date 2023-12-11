import os

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from dal.models.db_manager import DBManager
from payslips.routers.payslip_generation_router import payslip_generation_router


# Get environment variables
FASTAPI_HOST = os.environ["fastapi_host"]
SECRET_KEY = os.environ["JWT_SECRET_KEY"]

# App Initialization
payslip_app = FastAPI(tags=["payslip"])
payslip_app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


@payslip_app.on_event("startup")
def startup_db_client():
    stage = os.environ["STAGE"]
    DBManager.init(stage=stage, asset="ops-service")


@payslip_app.on_event("shutdown")
def shutdown_db_client():
    DBManager.terminate()


@payslip_app.get("/ping")
def ping():
    return {
        "status": "success",
        "message": "pong",
    }


payslip_app.include_router(payslip_generation_router)
