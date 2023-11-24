import functools
import json
import logging
import os
from bson import ObjectId
import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload

from dal.models.employees import Employee
from kyc.config import Config

GDRIVE_FOLDER_MIMETYPE = "application/vnd.google-apps.folder"
GDRIVE_FOLDER_URL_TEMPLATE = "https://drive.google.com/drive/folders/{folder_id}"
ROOT_FOLDER_DESCRIPTION_TEMPLATE = """
Name: {employeeName}
Mobile: {mobile}
Email: {email}
"""


class GoogleSheetsService:

    def __init__(self, sheet_id=None, logger=None) -> None:
        if logger is None:
            logger = logging.getLogger("drive_upload_service")
        self.logger = logger
        self._creds = service_account.Credentials.from_service_account_info(
            info=json.loads(Config.GOOGLE_CREDENTIALS),
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        self._sheets_service = build('sheets', 'v4', credentials=self._creds)
        self.sheet_id = sheet_id
        if self.sheet_id is None:
            self.sheet_id = Config.KYC_STATUS_GOOGLE_SHEETS_ID

    def encode_values(self, entries):
        encoded_entries = []
        for row in entries:
            encoded_row = []
            for value in row:
                if not isinstance(value, str):
                    encoded_row.append(str(value))
                else:
                    encoded_row.append(value)
            encoded_entries.append(encoded_row)
        return encoded_entries

    def append_entries(self, entries):
        return self._sheets_service.spreadsheets().values().append(
            spreadsheetId=self.sheet_id,
            range="RawEntries!A:A",
            body={"values": self.encode_values(entries)},
            valueInputOption="USER_ENTERED"
        ).execute()
