from datetime import timedelta

import pandas as pd

from dal.models.disbursement import Disbursements
from ops.models.employer_email_payload import EmployerDisbursementsEmailPayload


class EmployerDisbursementsFetchService:

    def __init__(self, employer_info: EmployerDisbursementsEmailPayload) -> None:
        self.employer_info = employer_info

    def _cursor_to_dataframe(self, cursor):
        return pd.DataFrame(list(cursor))

    def _process_df(self, df: pd.DataFrame):
        pass

    def _get_aggregation_pipeline(self, custom_filter={}, custom_projection={}):
        pipeline = [
            # get related disbursements
            {
                "$match": {
                    "employerId": self.employer_info.employer_id,
                    **custom_filter
                }
            },
            # fetch corresponding offer
            {
                "$lookup": {
                    "from": "offers",
                    "localField": "offerId",
                    "foreignField": "_id",
                    "as": "offer"
                },
            },
            {
                "$unwind": {
                    "path": "$offer",
                    "preserveNullAndEmptyArrays": False
                }
            },
            # fetch corresponding employment
            {
                "$lookup": {
                    "from": "employments",
                    "localField": "employmentId",
                    "foreignField": "_id",
                    "as": "employment"
                }
            },
            {
                "$unwind": {
                    "path": "$employment",
                    "preserveNullAndEmptyArrays": False
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "employerEmployeeId": "$employment.employerEmployeeId",
                    "bankAccountNumber": "$bankAccountNumber",
                    "loanAmount": "$loanAmount",
                    "utrNumber": "$bankReferenceNumber",
                    "amountCreditedDate": "$offer.disbursedAt",
                    "dueDate": "$dueDate",
                    **custom_projection
                }
            }
        ]

        return pipeline

    def _fetch_disbursements_df(self, custom_filter={}, custom_projection={}):
        pipeline = self._get_aggregation_pipeline(
            custom_filter=custom_filter, custom_projection=custom_projection)
        disbursements_result = Disbursements.aggregate(pipeline)

        # convert disbursements info to dataframe
        disbursements_df = self._cursor_to_dataframe(
            disbursements_result)

        # check if disbursements are present or not
        if not len(disbursements_df):
            return None

        return disbursements_df

    def fetch_daily_disbursements(self):
        custom_filter = {
            "updatedAt": {
                "$gte": self.employer_info.request_date
            }
        }
        custom_projection = {
            "status": "$status",
            "unipeEmployeeId": "$unipeEmployeeId"
        }

        daily_disbursements_df = self._fetch_disbursements_df(
            custom_filter, custom_projection)

        return daily_disbursements_df

    def fetch_monthly_disbursements(self):
        current_date = self.employer_info.request_date+timedelta(days=1)

        custom_filter = {
            "status": "SUCCESS",
            "$expr": {
                "$and": [
                    {
                        "$eq": [{"$year": "$updatedAt"}, current_date.year]
                    },
                    {
                        "$eq": [{"$month": "$updatedAt"}, current_date.month]
                    },
                ]
            },
        }

        monthly_disbursements_df = self._fetch_disbursements_df(custom_filter)

        return monthly_disbursements_df

    @staticmethod
    def fetch_csv_columns_map():
        csv_columns_map = {
            "_id": 0,
            "employerEmployeeId": "Employer Employee ID",
            "bankAccountNumber": "Bank Account Number",
            "loanAmount": "Loan Amount",
            "utrNumber": "UTR Number",
            "amountCreditedDate": "Amount Credited Date",
            "dueDate": "Due Date",
            "status": "Status",
            "unipeEmployeeId": "Unipe Employee ID"
        }

        return csv_columns_map
