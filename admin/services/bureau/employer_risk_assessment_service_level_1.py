import re
from datetime import datetime

from dateutil.relativedelta import relativedelta

from dal.models.employer_leads import EmployerLeads


class EmployerRiskAssessmentServiceLevel1:

    def __init__(self, stage, logger) -> None:
        self.stage = stage
        self.logger = logger

    def _fetch_score(self, report_data):
        score = int(report_data.get("scoreDetails", [{}])[0].get("value", 0))
        return score

    def _fetch_writeoff(self, report_data):
        retail_account_details = report_data.get("retailAccountDetails", [])
        writeoff = 0
        for retail_account in retail_account_details:
            current_writeoff = int(retail_account.get("writeOffAmount", 0))
            writeoff += current_writeoff

        return writeoff

    def _get_exact_dpd(self, payment_status):
        if payment_status is None:
            return 0

        pattern = re.compile(r'^\d+\+$')
        match = pattern.match(payment_status)
        if not match:
            return 0

        exact_dpd = int(payment_status[:-1])
        return exact_dpd

    def _is_valid_month(self, month_string, dpd_range_in_months):
        month, year = list(map(int, month_string.split("-")))
        test_date = datetime(year, month, 1)

        current_date = datetime.now()
        current_month, current_year = current_date.month, current_date.year
        reference_date = datetime(current_year, current_month, 1)

        time_difference = relativedelta(reference_date, test_date)
        return time_difference.months <= dpd_range_in_months

    def _fetch_dpd(self, report_data):
        retail_account_details = report_data.get("retailAccountDetails", [])

        dpd_6_months, dpd_2_years = 0, 0
        for retail_account in retail_account_details:
            payment_history = retail_account.get("history48Months", [])
            for monthly_history in payment_history:
                month_string = monthly_history["key"]
                payment_status = monthly_history["paymentStatus"]
                current_dpd = self._get_exact_dpd(payment_status)
                if self._is_valid_month(month_string=month_string, dpd_range_in_months=6) and current_dpd >= 30:
                    dpd_6_months += 1
                if self._is_valid_month(month_string=month_string, dpd_range_in_months=24) and current_dpd >= 90:
                    dpd_2_years += 1

        return dpd_6_months, dpd_2_years

    def generate_lead_summary(self, pan, data):
        report_data = data.get("data", {}).get("cCRResponse").get("cIRReportDataLst", [{}])[0].get(
            "cIRReportData")

        if not report_data:
            return

        dpd_6_months, dpd_2_years = self._fetch_dpd(report_data)
        summary = {
            EmployerLeads.SummaryFields.BUREAU_SCORE: self._fetch_score(report_data),
            EmployerLeads.SummaryFields.DPD_6_MONTHS: dpd_6_months,
            EmployerLeads.SummaryFields.DPD_2_YEARS: dpd_2_years,
            EmployerLeads.SummaryFields.WRITEOFF: self._fetch_writeoff(report_data),
        }
        self.update_lead_summary(pan, summary)

    def update_lead_summary(self, pan, summary=None):
        filter_ = {
            "pan": pan
        }
        if summary is None:
            summary = EmployerLeads.find_one(
                filter_=filter_,
                projection={
                    "_id": 0,
                    **{
                        summary_field: 1 for summary_field in EmployerLeads.SummaryFields.FIELD_LIST
                    }
                }
            )
        EmployerLeads.update(
            filter_=filter_,
            update={
                "$set": {
                    **summary,
                    "status": EmployerLeads.Status.SUCCESS
                }
            },
            upsert=False
        )
