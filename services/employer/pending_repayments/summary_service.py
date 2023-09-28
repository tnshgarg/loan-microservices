import pandas as pd

from dal.models.bank_accounts import BankAccounts
from dal.models.employer import Employer
from ops.models.employer_email_payload import EmployerEmailPayload


class EmployerPendingRepaymentsSummaryService:

    def __init__(self, employer_info: EmployerEmailPayload, pending_repayments_df: pd.DataFrame) -> None:
        self.employer_info = employer_info
        self.pending_repayments_df = pending_repayments_df

    def _get_company_name(self):
        employer_find_res = Employer.find_one(
            {
                "_id": self.employer_info.employer_id
            }
        )
        company_name = employer_find_res.get("companyName")

        return company_name

    def _get_total_due_amount(self):
        total_loan_amount = self.pending_repayments_df["loanAmount"].sum()
        total_paid_amount = self.pending_repayments_df["paidAmount"].sum()
        total_due_amount = total_loan_amount-total_paid_amount

        return total_due_amount

    def _get_repayment_account_details(self):
        bank_account_find_res = BankAccounts.find_one({
            "pId": self.employer_info.employer_id,
            "uType": "collectionAccount"
        })
        if bank_account_find_res is None:
            return {}
        bank_account_data = bank_account_find_res.get("data", {})

        beneficiary_name = bank_account_data.get("accountHolderName")
        account_number = bank_account_data.get("accountNumber")
        ifsc = bank_account_data.get("ifsc")

        repayment_account_details = {
            "beneficiary_name": beneficiary_name,
            "account_number": account_number,
            "ifsc": ifsc
        }
        return repayment_account_details

    def _convert_column_date_format(self, df, columns):
        for column in columns:
            df[column] = df[column].dt.strftime(
                "%d/%m/%Y")
        return

    def _get_summary_df(self):
        summary_columns = ["employerEmployeeId", "bankAccountNumber",
                           "loanAmount", "utrNumber", "amountCreditedDate", "dueDate"]
        new_summary_columns = ["Employee ID", "Bank Account Number",
                               "Loan Amount", "UTR Number", "Amount Credited Date", "Due Date"]

        summary_df = self.pending_repayments_df[summary_columns].copy()
        summary_df.columns = new_summary_columns

        self._convert_column_date_format(
            df=summary_df, columns=["Amount Credited Date", "Due Date"])

        return summary_df

    def fetch_pending_repayments_summary(self):
        company_name = self._get_company_name()
        total_due_amount = self._get_total_due_amount()
        due_date = self.employer_info.request_date.get_date_string()
        repayment_account_details = self._get_repayment_account_details()
        summary_df = self._get_summary_df()

        pending_repayments_summary = {
            "company_name": company_name,
            "total_due_amount": total_due_amount,
            "due_date": due_date,
            **repayment_account_details,
            "summary_df": summary_df
        }

        return pending_repayments_summary
