
from bson import ObjectId
from services.ewa.apollo.apollo_commercial_documentation_service import ApolloCommercialDocumentsService
from services.ewa.apollo.apollo_documentation_service import ApolloDocumentsService
from time import sleep


def generate_loan_documents(apollo_loan_payload):
    sleep(5)
    if apollo_loan_payload.loan_type == "COMMERCIAL":
        apollo_documents_service = ApolloCommercialDocumentsService(
            unipe_employee_id=ObjectId(apollo_loan_payload.unipe_employee_id),
            loan_application_id=ObjectId(
                apollo_loan_payload.loan_application_id),
            offer_id=ObjectId(apollo_loan_payload.offer_id)
        )
    else:
        apollo_documents_service = ApolloDocumentsService(
            unipe_employee_id=ObjectId(apollo_loan_payload.unipe_employee_id),
            loan_application_id=ObjectId(
                apollo_loan_payload.loan_application_id),
            offer_id=ObjectId(apollo_loan_payload.offer_id)
        )
    apollo_documents_service.generate_loan_documents()
