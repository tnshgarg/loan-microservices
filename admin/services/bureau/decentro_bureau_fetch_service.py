import datetime
import json
import os

import requests


class DecentroBureauFetchService:

    def __init__(self, stage, logger) -> None:
        self.stage = stage
        self.logger = logger
        decentro_config = json.loads(os.environ[f"decentro_{self.stage}"])
        self.headers = {
            "Content-Type": "application/json",
            "client_id": decentro_config["client_id"],
            "client_secret": decentro_config["client_secret"],
            "module_secret": decentro_config["module_secret"],
            "provider_secret": decentro_config["provider_secret"],
        }
        self.report_url = decentro_config["url"]["credit_report"]

    def fetch(self, pan, name, mobile, dob):

        current_timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

        json_object = {
            "reference_id": f"{pan}_{current_timestamp}",
            "consent": True,
            "consent_purpose": "Triggering Bureau Fetch for Personal Loan",
            "name": name,
            "date_of_birth": dob,
            "mobile": mobile,
            "inquiry_purpose": "PL",
            "document_type": "PAN",
            "document_id": pan,
        }

        res = requests.post(
            url=self.report_url,
            json=json_object,
            headers=self.headers
        )

        res_json = res.json()

        self.logger.info("decentro_api_res_status", extra={
            "res_status": res_json.get("status")
        })
        return res_json
