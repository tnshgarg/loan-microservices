

from datetime import datetime, timedelta
import json
from typing import Any, Dict, Optional
from fastapi import HTTPException

import requests

from kyc_service.config import Config


class ApolloApiException(HTTPException):

    def __init__(self, message: str) -> None:
        super().__init__(400, message)


class ApolloOauthService:

    def __init__(self) -> None:
        self.oauth_url = Config.APOLLO_CREDENTIALS["oauth_url"]
        self.client_id = Config.APOLLO_CREDENTIALS["client_id"]
        self.client_secret = Config.APOLLO_CREDENTIALS["client_secret"]
        self.token = None
        self.token_expiry = None

    def generate_token(self):
        token_req_payload = {'grant_type': 'client_credentials'}
        token_response = requests.post(
            self.oauth_url,
            data=token_req_payload,
            allow_redirects=False,
            auth=(
                self.client_id,
                self.client_secret)
        )
        if token_response.status_code == 200:
            token_details = token_response.json()
            self.token = token_details["access_token"]
            self.token_expiry = datetime.now(
            ) + timedelta(seconds=token_details["expires_in"])
            return self.token
        return None

    def fetch_token(self):
        if self.token is not None:
            if datetime.now() < self.token_expiry:
                return self.token
        return self.generate_token()


class ApolloAPI:
    def __init__(self) -> None:
        self.token_service = ApolloOauthService()
        self.base_url = Config.APOLLO_CREDENTIALS["base_url"]
        self.static_headers = {
            'x-api-key': Config.APOLLO_CREDENTIALS["api_key"],
            'Content-Type': 'application/json'
        }

    @property
    def headers(self):
        return {
            "Authorization": self.token_service.fetch_token(),
            **self.static_headers
        }

    def get_document_upload_link(self, partner_tag: str, partner_loan_id: str, document_key: str):
        response = requests.get(
            url=self.base_url+"/signed_url",
            headers=self.headers,
            params={
                "partner_tag": partner_tag,
                "loan_type": "ML",
                "partner_loan_id": partner_loan_id,
                "document_key": document_key,
            }
        )
        if response.status_code == 200:
            return response.json()
        raise ApolloApiException(
            f"API Failure: {response.status_code}: ```{response.text}```"
        )
