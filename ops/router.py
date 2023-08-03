import os
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Form, UploadFile
from typing_extensions import Annotated

from background_tasks.final_employer_approval import FinalEmployerApproval
from background_tasks.send_for_final_approval import SendForFinalApproval
from background_tasks.trigger_employer_approval import TriggerEmployerApproval
from ops.auth import get_user
from ops.forms.employer_approval_form import get_employer_approval_form
from ops.forms.final_approval_form import get_final_approval_form
from ops.models.cognito_sign_up import CognitoSignUp

# Get environment variables
STAGE = os.environ["stage"]

router = APIRouter(
    prefix=f"/{STAGE}/ops-service/employer-approval",
    tags=["employer-approval"]
)


@router.get("/ping")
def ping(abc: str, user: Optional[dict] = Depends(get_user)):
    return {
        "status": "success",
        "message": "pong",
        "abc": abc
    }


@router.post("/trigger")
def trigger_employer_approval(background_tasks: BackgroundTasks, cognito_sign_up_info: CognitoSignUp):
    handler_payload = {
        "cognito_sign_up_info": cognito_sign_up_info
    }
    background_tasks.add_task(TriggerEmployerApproval().run, handler_payload)

    return {
        "status": "SUCCESS",
        "message": "employer approval triggered"
    }


@router.get("/start")
def start_employer_approval(background_tasks: BackgroundTasks, employer_id: str, user: Optional[dict] = Depends(get_user)):

    return get_employer_approval_form(employer_id)


@router.post("/start-submit")
def submit_employer_approval_form(background_tasks: BackgroundTasks, employer_id: Annotated[str, Form()], notes: Annotated[str, Form()], files: List[UploadFile]):
    handler_payload = {
        "employer_id": employer_id,
        "notes": notes,
        "files": files
    }
    background_tasks.add_task(SendForFinalApproval().run, handler_payload)

    return {
        "status": "SUCCESS",
        "message": "employer approval form submitted"
    }


@router.get("/approve")
def approve_employer_approval(background_tasks: BackgroundTasks, employer_id: str, user: Optional[dict] = Depends(get_user)):

    return get_final_approval_form(employer_id)


@router.post("/approve-submit")
def submit_final_approval_form(background_tasks: BackgroundTasks, employer_id: Annotated[str, Form()], approve_or_deny: Annotated[str, Form()]):
    handler_payload = {
        "employer_id": employer_id,
        "approve_or_deny": approve_or_deny
    }
    background_tasks.add_task(FinalEmployerApproval().run, handler_payload)

    return {
        "status": "SUCCESS",
        "message": "final employer approval submitted"
    }
