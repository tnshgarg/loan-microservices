

from io import BytesIO
import os
from bson import ObjectId
from pyhtml2pdf import converter
from dal.models.employees import Employee
from dal.models.employer import Employer
from services.ewa.apollo.document_handling.loan_agreement_service import ApolloLoanAgreementService

from services.ewa.apollo.utils import convert_to_words
from services.storage.uploads.pdf_service import PDFService


class ApolloCommercialLoanAgreementService(ApolloLoanAgreementService):

    def __init__(self, loan_application_doc) -> None:
        super().__init__(loan_application_doc)
        self.employee = Employee.find_one({"_id": self.unipe_employee_id})
        self.employer = Employer.find_one({
            "commercialLoanDetails.keyPromoter": self.unipe_employee_id
        })
        promoters = self.employer["commercialLoanDetails"]["promoters"]
        promoter_2_id = None
        for promoter in promoters:
            if promoter == self.unipe_employee_id:
                continue
            promoter_2_id = promoter
            break
        self.employee_2 = Employee.find_one({
            "_id": promoter_2_id
        })
        if self.employee_2 is None:
            self.employee_2 = {}

    def generate_document(self) -> BytesIO:
        loan_agreement_template = open(
            "templates/html/ewa/apollo/commercial_loan_agreement.html"
        )
        template_str = loan_agreement_template.read()
        loan_agreement_html = template_str.format(
            todayDate=self.loan_info["disbursement_date"],
            district=self.customer_info["city"],
            LOCID=self.loc_id,
            limitAmount=str(self.loan_info["loan_amount"]) + "/-",
            locWords=convert_to_words(self.loan_info["loan_amount"]) + " only",
            LOCexpiryDate=self.loan_info["first_emi_date"],
            loanAmount=self.loan_info["loan_amount"],
            bankName=self.customer_info["customer_bank_name"],
            AccountNumber=self.customer_info["bank_account_number"],
            AccountHolderName=self.customer_info["customer_bank_account_name"],
            ifsc=self.customer_info["ifsc_code"],
            companyName=self.customer_info["first_name"],
            companyAddress=self.customer_info["address"],
            borrower1email=self.employee["email"],
            borrower1mobile=self.employee["mobile"],
            borrower1name=self.customer_info["directors_name"],
            borrower1address=self.employee["currentAddress"],
            borrower2name=self.employee_2.get("employeeName", ""),
            borrower2address=self.employee_2.get("currentAddress", ""),
            borrower2email=self.employee_2.get("email", ""),
            borrower2mobile=self.employee_2.get("mobile", ""),
        )

        return PDFService.html_to_pdf(f"{self.unipe_employee_id}_loan_agreement", loan_agreement_html)
