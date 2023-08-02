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
from kyc_service.config import Config

GDRIVE_FOLDER_MIMETYPE = "application/vnd.google-apps.folder"
GDRIVE_FOLDER_URL_TEMPLATE = "https://drive.google.com/drive/folders/{folder_id}"
ROOT_FOLDER_DESCRIPTION_TEMPLATE = """
Name: {employeeName}
Mobile: {mobile}
Email: {email}
"""


class DriveUploadService:

    def __init__(self, base_folder_id=None, logger=None) -> None:
        if logger is None:
            logger = logging.getLogger("drive_upload_service")
        self.logger = logger
        self._creds = service_account.Credentials.from_service_account_info(
            info=json.loads(Config.GOOGLE_CREDENTIALS),
            scopes=['https://www.googleapis.com/auth/drive']
        )
        self._drive_service = build('drive', 'v3', credentials=self._creds)
        self.base_folder_id = base_folder_id
        if self.base_folder_id is None:
            self.base_folder_id = Config.GDRIVE_BASE_FOLDER_ID

    def get_description(self, unipe_employee_id: str):
        employee_doc = Employee.find_one({"_id": ObjectId(unipe_employee_id)})
        return ROOT_FOLDER_DESCRIPTION_TEMPLATE.format(**employee_doc)

    def upload_file(self, unipe_employee_id, name, mime_type, fd, description=""):
        parent_folder = self.get_or_create_employee_root(unipe_employee_id)
        file_metadata = {
            'name': name,
            'parents': [parent_folder],
            'description': description
        }
        fd.seek(0)
        media = MediaIoBaseUpload(fd, mimetype=mime_type)
        # pylint: disable=maybe-no-member
        file_upload_response = self._drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        file_upload_response["folderUrl"] = GDRIVE_FOLDER_URL_TEMPLATE.format(
            folder_id=parent_folder)
        return file_upload_response

    @functools.lru_cache(maxsize=512)
    def get_or_create_employee_root(self, unipe_employee_id: str):
        file_search_response = self._drive_service.files().list(
            q=f"mimeType='{GDRIVE_FOLDER_MIMETYPE}' and name = '{unipe_employee_id}' and '{self.base_folder_id}' in parents",
            spaces='drive',
            fields='nextPageToken,'
            'files(id, name)'
        ).execute()
        files = file_search_response["files"]
        if (len(files)):
            return files[0]["id"]
        else:
            return self.create_employee_root(unipe_employee_id)

    def get_employee_root_url(self, unipe_employee_id: str):
        return GDRIVE_FOLDER_URL_TEMPLATE.format(folder_id=self.get_or_create_employee_root(unipe_employee_id))

    def create_employee_root(self, unipe_employee_id: str):
        file_metadata = {
            'name': unipe_employee_id,
            'mimeType': GDRIVE_FOLDER_MIMETYPE,
            'description': self.get_description(unipe_employee_id),
            'parents': [self.base_folder_id]
        }
        # pylint: disable=maybe-no-member
        employee_folder = self._drive_service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()
        folder_id = employee_folder.get('id')
        self.logger.info(
            f"gdrive_create_employee_root: {json.dumps({'unipeEmployeeId': unipe_employee_id, 'folder_id': folder_id})}"
        )
        return folder_id
