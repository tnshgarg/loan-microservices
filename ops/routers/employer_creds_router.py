import os
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Form
from typing_extensions import Annotated
from background_tasks.employer_creds.save_employer_creds import SaveEmployerCreds
from ops.auth import get_user
from ops.forms.cashfree_payouts_creds_form import get_employer_creds_form
from ops.forms.form_submit_response import get_form_submit_response
from ops.utils.privilege_level import is_sales_user_privileged

STAGE = os.environ["STAGE"]

employer_creds_router = APIRouter(
    prefix=f"/employer-creds",
    tags=["employer-creds"]
)


@employer_creds_router.get("/ping")
def ping():
    return {
        "status": "success",
        "message": "pong",
    }

@employer_creds_router.get("/add-creds")
def start_employer_approval(background_tasks: BackgroundTasks,
                            employer_id: str,
                            user: Optional[dict] = Depends(get_user)):

    return get_employer_creds_form(employer_id)

@employer_creds_router.post("/submit-creds")
def submit_final_creds_form(background_tasks: BackgroundTasks,
                               employer_id: Annotated[str, Form()],
                               portal: Annotated[str, Form()],
                               username: Annotated[str, Form()],
                               password: Annotated[str, Form()],
                               public_key: Annotated[str, Form()],
                               user: Optional[dict] = Depends(get_user)):
    user_email = user["email"]
    if not is_sales_user_privileged(user_email):
        return get_form_submit_response("Not Authorized to Update Employer Creds")

    handler_payload = {
        "employer_id": employer_id,
        "portal": portal,
        "username": username,
        "password": password,
        "public_key": public_key,
    }

    background_tasks.add_task( SaveEmployerCreds().run, handler_payload )

    return get_form_submit_response("Employer creds Submitted Successfully")
