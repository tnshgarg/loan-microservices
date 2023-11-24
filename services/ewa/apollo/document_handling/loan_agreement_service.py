

from io import BytesIO
import os
from bson import ObjectId
from pyhtml2pdf import converter

from services.ewa.apollo.utils import convert_to_words
from services.storage.uploads.pdf_service import PDFService


class ApolloLoanAgreementService:

    def __init__(self, loan_application_doc) -> None:
        self.unipe_employee_id = loan_application_doc["unipeEmployeeId"]
        self.loan_info = loan_application_doc["data"]["payloads"]["loc"]["loan_information"]
        self.customer_info = loan_application_doc["data"]["payloads"]["loc"]["customer_information"]
        self.loc_id = loan_application_doc["externalLoanId"]

    def generate_document(self) -> BytesIO:
        loan_agreement_template = open(
            "templates/html/ewa/apollo/loan_agreement.html"
        )
        template_str = loan_agreement_template.read()
        loan_agreement_html = template_str.format(
            todayDate=self.loan_info["disbursement_date"],
            district=self.customer_info["city"],
            LOCID=self.loc_id,
            limitAmount=str(self.loan_info["loan_amount"]) + "/-",
            locWords=convert_to_words(self.loan_info["loan_amount"]) + " only",
            panName=self.customer_info["first_name"] +
            " " + self.customer_info["last_name"],
            address=self.customer_info["address"],
            email=self.customer_info["email"],
            mobileNumber=self.customer_info["phone"],
            LOCexpiryDate=self.loan_info["first_emi_date"],
            loanAmount=self.loan_info["loan_amount"],
            bankName=self.customer_info["customer_bank_name"],
            AccountNumber=self.customer_info["bank_account_number"],
            AccountHolderName=self.customer_info["customer_bank_account_name"],
            ifsc=self.customer_info["ifsc_code"],
        )

        return PDFService.html_to_pdf(f"{self.unipe_employee_id}_loan_agreement", loan_agreement_html)
