import json
import os

import requests


class KarzaApi:

    def __init__(self) -> None:
        self.karza_assets = json.loads(
            os.environ.get(f"karza_assets", "{}"))
        self.base_url = self.karza_assets.get("base_url")
        self.api_key = self.karza_assets.get("key")
        self.headers = {
            "Content-Type": "application/json",
            "x-karza-key": self.api_key
        }

    def pan_fetch_details(self, pan_number: str):
        url = f'{self.base_url}/{self.karza_assets.get("xpath", {}).get("pan_fetch_details")}'
        payload = {
            "pan": pan_number,
            "lite": "Y",
            "consent": "Y"
        }
        response = requests.post(
            url=url,
            headers=self.headers,
            json=payload
        )
        return response.status_code, response.json()
