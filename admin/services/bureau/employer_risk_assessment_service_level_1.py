import re

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

    # for dpd calculation, use freq of dpd , generate a map of dpd values for all 48 months
    # key parsing of history mm-yy, take -6 and -24 from current time T
    def _fetch_dpd(self, report_data):
        retail_account_details = report_data.get("retailAccountDetails", [])

        dpd_6_months, dpd_2_years = 0, 0
        for retail_account in retail_account_details:
            payment_history = retail_account.get("history48Months", [])
            for index in range(min(6, len(payment_history))):
                payment_status = payment_history[index].get("paymentStatus")
                dpd_6_months += self._get_exact_dpd(payment_status)
            dpd_2_years = dpd_6_months

            if len(payment_history) > 6:
                for index in range(6, min(24, len(payment_history))):
                    payment_status = payment_history[index].get(
                        "paymentStatus")
                    dpd_2_years += self._get_exact_dpd(payment_status)

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
