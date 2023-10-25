from bson import ObjectId
from dal.models.employees import Employee
from kyc_service.services.ewa.apollo.apollo_service import ApolloDocumentsService
from kyc_service.services.ewa.apollo.schema import ApolloLoanPayload
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


def upload_loc_creation_documents(apollo_loan_payload: ApolloLoanPayload):
    apollo_documents_service = ApolloDocumentsService(
        unipe_employee_id=ObjectId(apollo_loan_payload.unipe_employee_id),
        loan_application_id=ObjectId(apollo_loan_payload.loan_application_id),
        offer_id=ObjectId(apollo_loan_payload.offer_id)
    )
    apollo_documents_service.upload_loan_documents()
