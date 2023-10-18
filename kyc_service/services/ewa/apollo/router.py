from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, Field
from background_tasks.ewa.apollo.document_signing import sign_documents_and_upload
from background_tasks.ewa.apollo.loc_creation import upload_loc_creation_documents
from background_tasks.ewa.apollo.sl_kfs_download import download_loan_documents

from kyc_service.services.ewa.apollo.schema import ApolloLoanPayload


apollo_ewa_router = APIRouter()


@apollo_ewa_router.post("/upload/loc_documents")
def upload_loc_documents(background_tasks: BackgroundTasks, apollo_loan_payload: ApolloLoanPayload):
    background_tasks.add_task(
        upload_loc_creation_documents,
        apollo_loan_payload
    )
    return {
        "status": "SUCCESS",
        "message": "LOC documents are being uploaded"
    }


@apollo_ewa_router.post("/download/sl_kfs")
def download_sl_kfs(background_tasks: BackgroundTasks, apollo_loan_payload: ApolloLoanPayload):
    background_tasks.add_task(
        download_loan_documents,
        apollo_loan_payload
    )


@apollo_ewa_router.post("/upload/signed_documents")
def upload_signed_documents(background_tasks: BackgroundTasks, apollo_loan_payload: ApolloLoanPayload):
    background_tasks.add_task(
        sign_documents_and_upload,
        apollo_loan_payload
    )


@apollo_ewa_router.post("/upload/addendum")
def upload_addendum(background_tasks: BackgroundTasks, apollo_loan_payload: ApolloLoanPayload):
    background_tasks.add_task(
        sign_and_upload_addendum,
        apollo_loan_payload
    )
