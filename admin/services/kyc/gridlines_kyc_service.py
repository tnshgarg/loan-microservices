import re
from datetime import datetime

import bson

from dal.models.encrypted_bank_accounts import EncryptedBankAccounts
from services.kyc.gridlines import GridlinesApi


class GridlinesKYCService:

    def __init__(self, logger, stage, use_mock=False) -> None:
        self.logger = logger
        self.stage = stage
        self.ongrid_api = GridlinesApi(logger)

    def bank_verify_account(self, p_id, u_type, account_number, ifsc):
        filter_ = {
            "pId": p_id,
            "uType": u_type,
        }
        bank_account_data = {
            "accountNumber": account_number,
            "ifsc": ifsc
        }
        try:
            bank_verify_account_response = self.ongrid_api.bank_verify_account(
                account_number=account_number,
                ifsc=ifsc
            )

            if bank_verify_account_response.get("status") == 200:
                data = bank_verify_account_response.get("data", {})
                if data.get("code") == "1000":
                    account_holder_name = data["bank_account_data"].get("name")
                    bank_account_data["accountHolderName"] = re.sub(
                        '[^a-zA-Z0-9\n\.]', ' ', account_holder_name).strip()
                    bank_account_data["bankName"] = data["bank_account_data"]["bank_name"]
                    bank_account_data["branchName"] = data["bank_account_data"]["branch"]
                    bank_account_data["branchCity"] = data["bank_account_data"]["city"]
                    EncryptedBankAccounts.update_one(
                        filter_,
                        {
                            "$set": {
                                "accountNumber": account_number,
                                "verifyStatus": "INPROGRESS_CONFIRMATION",
                                "verifyMsg": data.get("message"),
                                "context.micr": data.get("bank_account_data").get("micr"),
                                "context.utr": data.get("bank_account_data").get("utr"),
                                "data": bank_account_data,
                                "verifyTimestamp": bank_verify_account_response.get("timestamp"),
                            }
                        }
                    )
                    return {
                        "status": 200,
                        "body": {
                            "verifyStatus": "INPROGRESS_CONFIRMATION",
                            "message": data.get("message"),
                            "data": bank_account_data,
                        }
                    }
                else:
                    EncryptedBankAccounts.update_one(
                        filter_,
                        {
                            "$set": {
                                "verifyStatus": "ERROR",
                                "verifyMsg": data.get("message"),
                                "data": bank_account_data,
                                "verifyTimestamp": bank_verify_account_response.get("timestamp"),
                            }
                        }
                    )
                    return {
                        "status": 400,
                        "body": {
                            "verifyStatus": "ERROR",
                            "message": data.get("message"),
                        }
                    }
            else:
                error = bank_verify_account_response.get(
                    "error", {}) or bank_verify_account_response.get("data", {})
                verify_msg = error.get(
                    "message") or bank_verify_account_response.get("message")
                EncryptedBankAccounts.update_one(
                    filter_,
                    {
                        "$set": {
                            "verifyStatus": "ERROR",
                            "verifyMsg": verify_msg,
                            "data": bank_account_data,
                            "verifyTimestamp": bank_verify_account_response.get("timestamp"),
                        }
                    }
                )
                return {
                    "status": 400,
                    "body": {
                        "verifyStatus": "ERROR",
                        "message": verify_msg
                    }
                }
        except Exception as e:
            EncryptedBankAccounts.update_one(
                filter_,
                {
                    "$set": {
                        "verifyStatus": "ERROR",
                        "verifyMsg": str(e),
                        "data": bank_account_data,
                        "verifyTimestamp": int(datetime.now().strftime('%s')),
                    }
                }
            )
            raise Exception(
                f"status_code=400,message={str(e)}"
            )
