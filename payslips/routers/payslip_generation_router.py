import os

from fastapi import APIRouter
from typing_extensions import Annotated

# Get environment variables
STAGE = os.environ["STAGE"]

payslip_generation_router = APIRouter(
    prefix=f"/generate-payslips",
    tags=["generate-payslips"]
)


@payslip_generation_router.get("/ping")
def ping():
    return {
        "status": "success",
        "message": "pong",
    }
