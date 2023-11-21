from datetime import timedelta

import pandas as pd

from dal.models.bank_accounts import BankAccounts
from dal.models.employer import Employer
from ops.models.employer_email_payload import EmployerDisbursementsEmailPayload


class EmployerDisbursementsSummaryService:

    def __init__(self, employer_info: EmployerDisbursementsEmailPayload, daily_disbursements_df: pd.DataFrame) -> None:
        self.employer_info = employer_info
        self.daily_disbursements_df = daily_disbursements_df
        self.daily_successful_disbursements_df = daily_disbursements_df[
            daily_disbursements_df["status"] == "SUCCESS"]

    def _get_company_name(self):
        employer_find_res = Employer.find_one(
            {
                "_id": self.employer_info.employer_id
            }
        )
        company_name = employer_find_res.get("companyName")

        return company_name

    def _get_current_date(self):
        current_date = self.employer_info.request_date+timedelta(days=1)
        current_date_string = current_date.strftime("%d/%m/%Y")
        current_month = current_date.month

        return current_date_string, current_month

    def _get_total_loan_amount(self):
        total_loan_amount = self.daily_successful_disbursements_df["loanAmount"].sum(
        )
        return total_loan_amount

    def _get_unique_employee_count(self):
        unique_employee_count = self.daily_successful_disbursements_df["unipeEmployeeId"].nunique(
        )
        return unique_employee_count

    def _get_due_date(self):
        min_due_date = self.daily_successful_disbursements_df["dueDate"].min()
        min_due_date_string = min_due_date.strftime("%d/%m/%Y")

        return min_due_date_string

    def _convert_column_date_format(self, df, columns):
        for column in columns:
            df[column] = df[column].dt.strftime(
                "%d/%m/%Y")
        return

    def successful_disbursements_summary_df(self):
        summary_columns = ["employerEmployeeId", "bankAccountNumber",
                           "loanAmount", "utrNumber", "amountCreditedDate", "dueDate"]
        new_summary_columns = ["Employee ID", "Bank Account Number",
                               "Loan Amount", "UTR Number", "Amount Credited Date", "Due Date"]

        summary_df = self.daily_successful_disbursements_df[summary_columns].copy(
        )
        summary_df.columns = new_summary_columns

        self._convert_column_date_format(
            df=summary_df, columns=["Amount Credited Date", "Due Date"])

        return summary_df

    def fetch_daily_disbursements_summary(self):
        company_name = self._get_company_name()
        current_date, current_month = self._get_current_date()
        total_loan_amount = self._get_total_loan_amount()
        unique_employee_count = self._get_unique_employee_count()
        due_date = self._get_due_date()
        successful_disbursements_summary_df = self.successful_disbursements_summary_df()

        disbursements_summary = {
            "company_name": company_name,
            "current_date": current_date,
            "current_month": current_month,
            "total_loan_amount": total_loan_amount,
            "unique_employee_count": unique_employee_count,
            "due_date": due_date,
            "successful_disbursements_summary_df": successful_disbursements_summary_df
        }

        return disbursements_summary
