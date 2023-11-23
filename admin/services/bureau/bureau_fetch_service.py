import json
import os
import traceback
from datetime import datetime

import bson
from dateutil.relativedelta import relativedelta

from admin.apis.karza_api import KarzaApi
from admin.services.bureau.bureau_report_generation_service import \
    BureauReportService
from admin.services.bureau.decentro_bureau_fetch_service import \
    DecentroBureauFetchService
from admin.services.bureau.employer_risk_assessment_service_level_1 import \
    EmployerRiskAssessmentServiceLevel1
from admin.services.bureau.s3_report_upload_service import S3ReportService
from dal.logger import get_app_logger
from dal.models.risk_profile import RiskProfile
from dal.utils import db_txn
from ops.exceptions.ops_exceptions import DevOpsException, OpsException


class BureauFetchService:

    def __init__(self):
        self.stage = os.environ["STAGE"]
        self.logger = get_app_logger("ops-microservice", self.stage)

    def _get_earlier_date(self):
        current_date = datetime.utcnow()
        earlier_date = current_date-relativedelta(months=6)
        return earlier_date

    def _fetch_dob(self, pan):
        status_code, pan_fetch_api_response = KarzaApi().pan_fetch_details(pan)

        if status_code != 200:
            raise Exception(
                f"Error in fetching PAN Info via Karza API with response - {pan_fetch_api_response}")

        dob = pan_fetch_api_response.get("result", {}).get("dob")
        return dob

    @db_txn
    def fetch_bureau_details(self, name, mobile, pan):
        dob = self._fetch_dob(pan)
        uType = "employer"

        filter_ = {
            "pan": pan,
            "uType": uType,
            "active": True,
            "_id": {
                "$gte": bson.ObjectId.from_datetime(self._get_earlier_date())
            }
        }

        projection = {"_id": 0, "bureau": 1,
                      "pass": 1, "provider": 1, "data": 1, "summary": 1}

        risk_profile_find_res = RiskProfile.find_one(filter_, projection)
        self.logger.info("risk_profile_find_res", extra={
            "data": risk_profile_find_res
        })

        if not risk_profile_find_res:
            bureau = "EQUIFAX"
            provider = "DECENTRO"

            data = DecentroBureauFetchService(self.stage, self.logger).fetch(
                pan, name, mobile, dob
            )
            json_data = json.dumps(data)

            S3ReportService(self.stage, self.logger).upload(json_data, pan,
                                                            provider, bureau)
            try:
                risk_profile_find_res = {
                    "pan": pan,
                    "uType": uType,
                    "active": True,
                    "bureau": bureau,
                    "data": data,
                    "provider": provider,
                }

                BureauReportService(self.stage, self.logger).generate(
                    risk_profile_find_res
                )
            except Exception as e:
                raise DevOpsException({
                    "reason": "report_generation_error",
                    "exception": traceback.format_exc(e)
                })
        else:
            EmployerRiskAssessmentServiceLevel1(
                self.stage, self.logger).update_lead_summary(pan)
            raise OpsException({
                "reason": "retried too soon",
                "previous_entry_filter": filter_
            })
