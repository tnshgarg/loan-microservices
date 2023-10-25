

from bson import ObjectId
from kyc_service.services.ewa.apollo.apollo_service import ApolloDocumentsService


def sign_and_upload_addendum(apollo_loan_payload):
    apollo_documents_service = ApolloDocumentsService(
        unipe_employee_id=ObjectId(apollo_loan_payload.unipe_employee_id),
        loan_application_id=ObjectId(apollo_loan_payload.loan_application_id),
        offer_id=ObjectId(apollo_loan_payload.offer_id)
    )
    apollo_documents_service.upload_signed_addendum()
