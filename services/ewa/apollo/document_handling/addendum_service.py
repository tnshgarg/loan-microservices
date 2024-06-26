

from datetime import datetime
from io import BytesIO
import math
import os
from bson import ObjectId
from services.ewa.apollo.constants import APOLLO_DATE_FORMAT


from services.ewa.apollo.utils import generate_loc_id
from services.storage.uploads.pdf_service import PDFService


class ApolloAddendumService:

    def __init__(self, loan_application_doc, offer_doc, type="personal") -> None:
        self.loan_info = loan_application_doc["data"]["payloads"]["loc"]["loan_information"]
        self.customer_info = loan_application_doc["data"]["payloads"]["loc"]["customer_information"]
        self.loc_id = loan_application_doc["externalLoanId"]
        self.partner_tag = "UFC" if type == "commercial" else "UEC"
        self.disbursement_id = loan_application_doc["data"]["nextDisbursementLoanId"]
        self.offer_doc = offer_doc
        self.loc_created_at = loan_application_doc["_id"].generation_time

    def calculate_apr(self, tenor, loan_amount, processing_fees):
        disbursed_amount = loan_amount - processing_fees
        apr = (100 * processing_fees/disbursed_amount) * (365 / tenor)
        return apr

    def generate_document(self) -> BytesIO:
        addendum_template = open("templates/html/ewa/apollo/addendum.html")
        template_str = addendum_template.read()
        today_date = datetime.now()
        tenor = (self.offer_doc["dueDate"] - today_date).days
        processing_fees = math.floor(self.offer_doc.get(
            'loanAmount') * 0.01 * self.offer_doc.get("fees"))
        APR = self.calculate_apr(
            tenor, self.offer_doc["loanAmount"], processing_fees)
        addendum_html = template_str.format(
            partner_loan_id=generate_loc_id(self.loc_id, self.partner_tag),
            loc_created_at=self.loc_created_at,
            disbursement_date=today_date.strftime(APOLLO_DATE_FORMAT),
            city=self.customer_info["city"],
            drawdownId=self.disbursement_id,
            borrower_name=self.customer_info["first_name"] +
            " " + self.customer_info["last_name"],
            aadhaar_address=self.customer_info["address"],
            email=self.customer_info["email"],
            limitAmount=self.loan_info["loan_amount"],
            eligibleAmount=self.offer_doc["eligibleAmount"],
            drawdownAmount=self.offer_doc["loanAmount"],
            balanceAmount=self.offer_doc["eligibleAmount"] -
            self.offer_doc["loanAmount"],
            processingFees=processing_fees,
            loanAmount=self.offer_doc["loanAmount"],
            APR="{:.02f} %".format(APR),
            repaymentDate=self.offer_doc["dueDate"].strftime(
                APOLLO_DATE_FORMAT),
            tenor=tenor,
            bankAccountNumber=self.customer_info["bank_account_number"],
            bankIFSC=self.customer_info["ifsc_code"],
            timestamp=today_date.isoformat(),
            disbursementDate=today_date.strftime(APOLLO_DATE_FORMAT),
        )
        return PDFService.html_to_pdf(f"{self.loc_id}_addendum", addendum_html)
