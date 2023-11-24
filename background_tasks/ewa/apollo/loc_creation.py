from bson import ObjectId
from services.ewa.apollo.apollo_commercial_documentation_service import ApolloCommercialDocumentsService
from services.ewa.apollo.apollo_documentation_service import ApolloDocumentsService
from services.ewa.apollo.schema import ApolloLoanPayload
from time import sleep


def upload_loc_creation_documents(apollo_loan_payload: ApolloLoanPayload):
    sleep(5)
    if apollo_loan_payload.loan_type == "COMMERCIAL":
        ApolloCommercialDocumentsService(
            unipe_employee_id=ObjectId(apollo_loan_payload.unipe_employee_id),
            loan_application_id=ObjectId(
                apollo_loan_payload.loan_application_id),
            offer_id=ObjectId(apollo_loan_payload.offer_id)
        ).upload_loan_documents()
    else:
        ApolloDocumentsService(
            unipe_employee_id=ObjectId(apollo_loan_payload.unipe_employee_id),
            loan_application_id=ObjectId(
                apollo_loan_payload.loan_application_id),
            offer_id=ObjectId(apollo_loan_payload.offer_id)
        ).upload_loan_documents()
