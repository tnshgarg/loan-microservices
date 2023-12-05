from datetime import datetime
from starlette.routing import Route, Router
from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException
from background_tasks.employer_emails.daily_disbursements_email import DailyDisbursementsEmail

from background_tasks.employer_emails.pending_repayments_email import PendingRepaymentsEmail
from ops.models.employer_email_payload import EmployerRepaymentsEmailPayload


async def parse_employer_info(request: Request) -> EmployerRepaymentsEmailPayload:
    request = await request.json()
    return EmployerRepaymentsEmailPayload(
        employerId=request["employerId"],
        requestDate=request["requestDate"]
    )


async def repayment_reminder(request: Request):
    employer_info = await parse_employer_info(request)
    task = BackgroundTask(PendingRepaymentsEmail().run, payload={
                          "employer_info": employer_info})
    return JSONResponse({
        "status": "SUCCESS",
        "message": f"{employer_info.employer_id}: repayments_reminder triggered",
    }, background=task)


async def disbursements_summary(request):
    employer_info = await parse_employer_info(request)
    task = BackgroundTask(DailyDisbursementsEmail().run, payload={
                          "employer_info": employer_info})
    return JSONResponse({
        "status": "SUCCESS",
        "message": f"{employer_info.employer_id}: disbursement summary triggered",
    }, background=task)


employer_emails_router = Router(
    routes=[
        Route(path="/repayments",
              endpoint=repayment_reminder, methods=["POST"]),
        Route(path="/disbursements",
              endpoint=disbursements_summary, methods=["POST"]),
    ]
)
