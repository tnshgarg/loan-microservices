import pandas as pd

from dal.models.repayment import Repayments
from ops.models.employer_email_payload import EmployerEmailPayload


class EmployerPendingRepaymentsService:

    def __init__(self, employer_info: EmployerEmailPayload) -> None:
        self.employer_info = employer_info

    def _cursor_to_dataframe(self, cursor):
        return pd.DataFrame(list(cursor))

    def _process_df(self, df: pd.DataFrame):
        pass

    def _get_aggregation_pipeline(self):
        pipeline = [
            # get related repayments
            {
                "$match": {
                    "$expr": {
                        "$and": [
                            {
                                "$eq": ["$employerId", self.employer_info.employer_id]
                            },
                            {
                                "$eq": [{"$year": "$dueDate"}, self.employer_info.request_date.year]
                            },
                            {
                                "$eq": [{"$month": "$dueDate"}, self.employer_info.request_date.month]
                            },
                            {
                                "$eq": [{"$dayOfMonth": "$dueDate"}, self.employer_info.request_date.day]
                            },
                            {
                                "$lt": ["$paidAmount", "$amount"]
                            }
                        ]
                    }
                }
            },
            # fetch corresponding offer
            {
                "$lookup": {
                    "from": "offers",
                    "localField": "_id",
                    "foreignField": "repaymentId",
                    "as": "offer"
                },
            },
            {
                "$unwind": {
                    "path": "$offer",
                    "preserveNullAndEmptyArrays": False
                }
            },
            # fetch corresponding disbursement
            {
                "$lookup": {
                    "from": "disbursements",
                    "localField": "offer._id",
                    "foreignField": "offerId",
                    "as": "disbursement"
                },
            },
            {
                "$unwind": {
                    "path": "$disbursement",
                    "preserveNullAndEmptyArrays": False
                }
            },
            # fetch corresponding employee info
            {
                "$lookup": {
                    "from": "employees",
                    "localField": "unipeEmployeeId",
                    "foreignField": "_id",
                    "as": "employee"

                }
            },
            {
                "$unwind": {
                    "path": "$employee",
                    "preserveNullAndEmptyArrays": False
                }
            },
            # fetch corresponding bank account
            {
                "$lookup": {
                    "from": "bankAccounts",
                    "localField": "unipeEmployeeId",
                    "foreignField": "pId",
                    "as": "bankAccount"
                }
            },
            {
                "$unwind": {
                    "path": "$bankAccount",
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
            # project required information
            {
                "$project": {
                    "_id": 0,
                    "name": "$employee.employeeName",
                    "number": "$employee.mobile",
                    "email": "$employee.email",
                    "bankAccountNumber": "$bankAccount.data.accountNumber",
                    "ifscCode": "$bankAccount.data.ifsc",
                    "loanAmount": "$disbursement.loanAmount",
                    "utrNumber": "$disbursement.bankReferenceNumber",
                    "offerAvailedDate": "$offer.availedAt",
                    "amountCreditedDate": "$offer.disbursedAt",
                    "dueDate": "$dueDate",
                    "employerEmployeeId": "$employment.employerEmployeeId"
                }
            }
        ]

        return pipeline

    def fetch_pending_repayments(self):
        # perform aggregation query
        pipeline = self._get_aggregation_pipeline()
        pending_repayments_result = Repayments.aggregate(pipeline)

        # convert repayments info to dataframe
        pending_repayments_df = self._cursor_to_dataframe(
            pending_repayments_result)

        # check if pending repayments are present or not
        if not len(pending_repayments_df):
            return None

        return pending_repayments_df
