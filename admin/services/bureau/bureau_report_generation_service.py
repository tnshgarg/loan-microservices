import datetime
import json

from admin.services.bureau.employer_lead_service import EmployerLeadService
from dal.models.risk_profile import RiskProfile


class BureauReportService:

    def __init__(self, stage, logger) -> None:
        self.stage = stage
        self.logger = logger

    @staticmethod
    def summarize_write_offs(data, pass_):
        write_offs_summary = {
            "value": str(data["retailAccountsSummary"]["noOfWriteOffs"]),
            "status": "SUCCESS",
            "reason": "Zero WriteOffs",
        }
        if str(data["retailAccountsSummary"]["noOfWriteOffs"]) != "0":
            pass_ = "DECLINED"
            write_offs_summary["status"] = pass_
            write_offs_summary["reason"] = "Non-zero WriteOffs"

        return write_offs_summary, pass_

    @staticmethod
    def summarize_score(data, pass_):
        score_summary = {
            "value": int(data["scoreDetails"][0]["value"]),
            "status": "SUCCESS",
            "reason": "Greater Than 600",
        }
        if int(data["scoreDetails"][0]["value"]) <= 600:
            pass_ = "DECLINED"
            score_summary["status"] = pass_
            score_summary["reason"] = "Less Than 600"

        return score_summary, pass_

    @staticmethod
    def summarize_asset_classification_status(data, pass_):
        asset_classification_statuses = BureauReportService._get_values(
            "assetClassificationStatus", data)
        allowed_values = ["standard", "std", "*"]
        asset_classification_summary = {
            "value": list(asset_classification_statuses),
            "status": "SUCCESS",
            "reason": "Standard Asset Classification Status",
        }
        if any(val not in allowed_values for val in asset_classification_statuses):
            pass_ = "DECLINED"
            asset_classification_summary["status"] = pass_
            asset_classification_summary["reason"] = "Non-Standard Asset Classification Status"

        return asset_classification_summary, pass_

    @staticmethod
    def summarize_suit_filed_status(data, pass_):
        suit_filed_statuses = BureauReportService._get_values(
            "suitFiledStatus", data)
        allowed_values = ["standard", "std", "*"]
        suit_filed_status_summary = {
            "value": list(suit_filed_statuses),
            "status": "SUCCESS",
            "reason": "Standard Suit Filed Status",
        }
        if any(val not in allowed_values for val in suit_filed_statuses):
            pass_ = "DECLINED"
            suit_filed_status_summary["status"] = pass_
            suit_filed_status_summary["reason"] = "Non-Standard Suit Filed Status"

        return suit_filed_status_summary, pass_

    @staticmethod
    def _get_values(key, d):
        return {
            month[key].lower()
            for retail_account in d["retailAccountDetails"]
            for month in retail_account.get("history48Months", [])
        } | {
            month[key].lower()
            for retail_account in d["retailAccountDetails"]
            for month in retail_account.get("history24Months", [])
        }

    def _decompress_string(self, msg_bytes):
        import zlib
        msg_bytes = zlib.decompress(msg_bytes)
        msg = msg_bytes.decode('utf-8')
        return msg

    def generate(self, risk_profile_find_result):
        pass_ = "SUCCESS"
        summary = risk_profile_find_result.get("summary", {})

        print("risk_profile_result", risk_profile_find_result)

        if risk_profile_find_result["bureau"] == "EQUIFAX":
            if risk_profile_find_result.get("pass"):
                pass_ = risk_profile_find_result.get("pass")
            else:
                if type(risk_profile_find_result["data"]) == bytes:
                    risk_profile_find_result["data"] = json.loads(
                        self._decompress_string(risk_profile_find_result["data"]))

                summary["apiResponse"] = {
                    "value": risk_profile_find_result["data"]["responseCode"],
                    "status": risk_profile_find_result["data"]["status"],
                    "reason": risk_profile_find_result["data"]["message"],
                }

                if risk_profile_find_result["data"]["status"] != "SUCCESS":
                    pass_ = "DECLINED"

                try:
                    data = risk_profile_find_result["data"]["data"]["cCRResponse"]["cIRReportDataLst"][0].get(
                        "cIRReportData")
                    if data is None:
                        pass_ = "DECLINED"
                    else:
                        summary["noOfWriteOffs"], pass_ = self.summarize_write_offs(
                            data, pass_)
                        summary["score"], pass_ = self.summarize_score(
                            data, pass_)
                        summary["assetClassificationStatus"], pass_ = self.summarize_asset_classification_status(
                            data, pass_)
                        summary["suitFiledStatus"], pass_ = self.summarize_suit_filed_status(
                            data, pass_)

                except Exception as e:
                    print(e)

        risk_profile_find_result["summary"] = summary

        if risk_profile_find_result.get("data") and risk_profile_find_result.get("uType") != "employer":
            del risk_profile_find_result["data"]

        risk_profile_find_result["pass"] = pass_
        risk_profile_find_result["updatedAt"] = datetime.datetime.now()

        risk_profile_insert_res = RiskProfile.insert_one(
            risk_profile_find_result)
        self.logger.info("risk_profile_insert_res", extra={
            "data": risk_profile_insert_res
        })

        pan = risk_profile_find_result["pan"]
        data = risk_profile_find_result["data"]
        EmployerLeadService(
            self.stage, self.logger).generate_lead_summary(pan, data)
