import os

from fastapi import APIRouter, BackgroundTasks, Depends

from background_tasks.employer_emails.daily_disbursements_email import \
    DailyDisbursementsEmail
from background_tasks.employer_emails.pending_repayments_email import \
    PendingRepaymentsEmail
from ops.api_key_auth import get_api_key
from ops.models.employer_email_payload import (
    EmployerDisbursementsEmailPayload, EmployerRepaymentsEmailPayload)

# Get environment variables
STAGE = os.environ["STAGE"]

employer_emails_router = APIRouter(
    prefix=f"/{STAGE}/ops-service/employer-emails",
    tags=["employer-emails"]
)


@employer_emails_router.get("/ping")
def ping():
    return {
        "status": "success",
        "message": "pong",
    }


@employer_emails_router.post("/repayments")
def send_email_for_pending_repayments(background_tasks: BackgroundTasks,
                                      employer_info: EmployerRepaymentsEmailPayload,
                                      api_key: str = Depends(get_api_key)):
    handler_payload = {
        "employer_info": employer_info
    }
    background_tasks.add_task(PendingRepaymentsEmail().run, handler_payload)
    return {
        "status": "SUCCESS",
        "message": "employer mail for repayments triggered",
    }


@employer_emails_router.post("/disbursements")
def send_email_for_pending_repayments(background_tasks: BackgroundTasks,
                                      employer_info: EmployerDisbursementsEmailPayload,
                                      api_key: str = Depends(get_api_key)):
    handler_payload = {
        "employer_info": employer_info
    }
    background_tasks.add_task(DailyDisbursementsEmail().run, handler_payload)
    return {
        "status": "SUCCESS",
        "message": "employer mail for repayments triggered",
    }
