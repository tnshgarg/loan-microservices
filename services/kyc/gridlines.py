
import json
from base64 import b64encode
from kyc.config import Config
import requests


class GridlinesApi:

    def __init__(self, logger) -> None:
        self.logger = logger
        self.ongrid_assets = json.loads(Config.GRIDLINES)
        self.base_url = self.ongrid_assets.get("base_url")
        self.headers = {
            "Content-Type": "application/json",
            "X-Auth-Type": "API-Key",
            "X-API-Key": self.ongrid_assets.get("api_key")
        }

    def aadhaar_ocr(self, file):
        file.seek(0)
        file_base64 = b64encode(file.read()).decode()
        response = requests.post(
            url=f"{self.base_url}/aadhaar-api/ocr",
            headers=self.headers,
            json={
                "base64_data": file_base64,
                "consent": "Y"
            }
        )

        status_code = response.status_code
        body = response.json()
        return status_code, body

    def verify_bank_account(self, account_number, ifsc):
        url = f'{self.base_url}/bank-api/verify'
        self.logger.info("bank_verify_account_url", extra={
            "data": {"url": url}
        })
        response = requests.post(
            url=url,
            headers=self.headers,
            json={
                "account_number": account_number,
                "ifsc": ifsc,
                "consent": "Y",
            }
        )
        response_json = response.json()
        self.logger.info("bank_verify_account_res", extra={
            "data": response_json
        })
        return response_json
