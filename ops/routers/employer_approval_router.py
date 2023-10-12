import os
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Form, UploadFile
from typing_extensions import Annotated

from background_tasks.employer_approval.final_employer_approval import \
    FinalEmployerApproval
from background_tasks.employer_approval.send_for_final_approval import \
    SendForFinalApproval
from background_tasks.employer_approval.trigger_employer_approval import \
    TriggerEmployerApproval
from ops.auth import get_user
from ops.forms.employer_approval_form import get_employer_approval_form
from ops.forms.final_approval_form import get_final_approval_form
from ops.forms.form_submit_response import get_form_submit_response
from ops.models.cognito_sign_up import CognitoSignUp
from ops.utils.privilege_level import is_sales_user_privileged

# Get environment variables
STAGE = os.environ["STAGE"]

employer_approval_router = APIRouter(
    prefix=f"/{STAGE}/ops-service/employer-approval",
    tags=["employer-approval"]
)


@employer_approval_router.get("/ping")
def ping():
    return {
        "status": "success",
        "message": "pong",
    }


@employer_approval_router.post("/trigger")
def trigger_employer_approval(background_tasks: BackgroundTasks,
                              cognito_sign_up_info: CognitoSignUp):
    handler_payload = {
        "cognito_sign_up_info": cognito_sign_up_info
    }
    background_tasks.add_task(TriggerEmployerApproval().run, handler_payload)

    return {
        "status": "SUCCESS",
        "message": "employer approval triggered"
    }


@employer_approval_router.get("/start")
def start_employer_approval(background_tasks: BackgroundTasks,
                            employer_id: str,
                            user: Optional[dict] = Depends(get_user)):

    return get_employer_approval_form(employer_id)


@employer_approval_router.post("/start-submit")
def submit_employer_approval_form(background_tasks: BackgroundTasks,
                                  employer_id: Annotated[str, Form()],
                                  notes: Annotated[str, Form()],
                                  agreement: UploadFile,
                                  pan: UploadFile,
                                  gst: UploadFile,
                                  user: Optional[dict] = Depends(get_user)):
    handler_payload = {
        "employer_id": employer_id,
        "notes": notes,
        "files": [agreement, pan, gst]
    }
    background_tasks.add_task(SendForFinalApproval().run, handler_payload)

    return get_form_submit_response("Employer Approval Form Submitted Successfully")


@employer_approval_router.get("/approve")
def approve_employer_approval(background_tasks: BackgroundTasks, employer_id: str, user: Optional[dict] = Depends(get_user)):
    return get_final_approval_form()


@employer_approval_router.post("/approve-submit")
def submit_final_approval_form(background_tasks: BackgroundTasks,
                               employer_id: Annotated[str, Form()],
                               approve_or_deny: Annotated[str, Form()],
                               user: Optional[dict] = Depends(get_user)):
    user_email = user["email"]
    if not is_sales_user_privileged(user_email):
        return get_form_submit_response("Not Authorized to Approve Employer")

    handler_payload = {
        "employer_id": employer_id,
        "approve_or_deny": approve_or_deny
    }
    background_tasks.add_task(FinalEmployerApproval().run, handler_payload)

    return get_form_submit_response("Final Employer Approval Submitted Successfully")
