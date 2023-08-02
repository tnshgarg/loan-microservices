import os
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends

from background_tasks.approve_employer_approval import ApproveEmployerApproval
from background_tasks.deny_employer_approval import DenyEmployerApproval
from background_tasks.start_employer_approval import StartEmployerApproval
from background_tasks.trigger_employer_approval import TriggerEmployerApproval
from ops.auth import get_user
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
def start_employer_approval(background_tasks: BackgroundTasks, employer_id: str):
    handler_payload = {
        "employer_id": employer_id
    }
    background_tasks.add_task(StartEmployerApproval().run, handler_payload)
    return {
        "status": "SUCCESS",
        "message": "employer approval started"
    }


@router.get("/approve")
def approve_employer_approval(background_tasks: BackgroundTasks, employer_id: str):
    handler_payload = {
        "employer_id": employer_id
    }
    background_tasks.add_task(ApproveEmployerApproval().run, handler_payload)
    return {
        "status": "SUCCESS",
        "message": "employer approval done"
    }


@router.get("/deny")
def deny_employer_approval(background_tasks: BackgroundTasks, employer_id: str):
    handler_payload = {
        "employer_id": employer_id
    }
    background_tasks.add_task(DenyEmployerApproval().run, handler_payload)
    return {
        "status": "SUCCESS",
        "message": "employer approval denied"
    }
