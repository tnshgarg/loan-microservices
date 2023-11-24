from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, Field
from background_tasks.ewa.apollo.document_signing import sign_documents_and_upload
from background_tasks.ewa.apollo.loc_creation import upload_loc_creation_documents
from background_tasks.ewa.apollo.sl_kfs_download import generate_loan_documents

from services.ewa.apollo.schema import ApolloLoanPayload


liquiloans_ewa_router = APIRouter()


@liquiloans_ewa_router.post("/download/loan_documents")
def upload_loc_documents(background_tasks: BackgroundTasks, apollo_loan_payload: ApolloLoanPayload):
    background_tasks.add_task(
        upload_loc_creation_documents,
        apollo_loan_payload
    )
    return {
        "status": "SUCCESS",
        "message": "LOC documents are being uploaded"
    }


@liquiloans_ewa_router.post("/upload/signed_documents")
def upload_loc_documents(background_tasks: BackgroundTasks, apollo_loan_payload: ApolloLoanPayload):
    background_tasks.add_task(
        upload_loc_creation_documents,
        apollo_loan_payload
    )
    return {
        "status": "SUCCESS",
        "message": "LOC documents are being uploaded"
    }
