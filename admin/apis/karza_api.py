import json
import os

import requests

from kyc.config import Config


class KarzaApi:

    def __init__(self) -> None:
        self.karza_assets = Config.KARZA
        self.base_url = self.karza_assets.get("base_url")
        self.api_key = self.karza_assets.get("api_key")
        self.headers = {
            "Content-Type": "application/json",
            "x-karza-key": self.api_key
        }

    def pan_fetch_details(self, pan_number: str):
        url = f'{self.base_url}/v3/pan-profile'
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
