
from base64 import b64encode
from datetime import datetime
import io
import json
from typing import Annotated
import bson
from fastapi import Depends
from dal.models.employees import Employee
from dal.models.government_ids import GovernmentIds
from dal.utils import db_txn
from kyc_service.config import Config
from kyc_service.dependencies.kyc import gdrive_upload_service, gridlines_api, s3_upload_service
from kyc_service.services.kyc.gridlines import GridlinesApi
from kyc_service.services.storage.sheets.google_sheets import GoogleSheetsService
from kyc_service.services.storage.uploads.drive_upload_service import DriveUploadService
from kyc_service.services.storage.uploads.s3_upload_service import S3UploadService


class MediaUploadService:

    def __init__(self,
                 unipe_employee_id: bson.ObjectId,
                 sales_user_id: bson.ObjectId,
                 gdrive_upload_service: DriveUploadService,
                 s3_upload_service: S3UploadService,
                 google_sheets_service: GoogleSheetsService
                 ) -> None:
        self.unipe_employee_id = unipe_employee_id
        self.sales_user_id = sales_user_id
        self.gdrive_upload_service = gdrive_upload_service
        self.s3_upload_service = s3_upload_service
        self.google_sheets_service = google_sheets_service
        now = datetime.now()
        self.ts_prefix = now.strftime("%Y_%m_%d_%H_%M")
        self.ts_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
        self.employee_doc = Employee.find_one({"_id": unipe_employee_id})
        self.common_columns = [self.ts_datetime, self.employee_doc['mobile'], self.employee_doc['employeeName'],
                               str(self.sales_user_id)]

    @staticmethod
    def _parse_extension(content_type):
        ctypes = content_type.split(";")
        mime = ctypes[0]
        extension = mime.split("/")[1]
        return extension

    def _upload_media(self, form_file, filename):
        file_extension = self._parse_extension(form_file.content_type)
        drive_upload_response = self.gdrive_upload_service.upload_file(
            str(self.unipe_employee_id),
            f"{self.ts_prefix}_{filename}.{file_extension}",
            mime_type=form_file.content_type,
            fd=form_file.file,
            description=f"Unipe Employee Id: {self.unipe_employee_id} \n Sales User: {self.sales_user_id}"
        )
        self.s3_upload_service.upload(
            key=f"{self.unipe_employee_aadhaarViewLink}",
            fd=form_file.file
        )
        return drive_upload_response["webViewLink"]

    def _upload_text(self, text, filename):
        dummy_file = io.StringIO(text)
        drive_upload_response = self.gdrive_upload_service.upload_file(
            str(self.unipe_employee_id),
            f"{self.ts_prefix}_{filename}.txt",
            mime_type="text/plain",
            fd=dummy_file,
            description=f"Unipe Employee Id: {self.unipe_employee_id} \n Sales User: {self.sales_user_id}"
        )
        self.s3_upload_service.upload(
            key=f"/kyc-service/{self.unipe_employee_id}/{self.ts_prefix}_{filename}.txt",
            fd=dummy_file
        )
        return drive_upload_response["webViewLink"]

    def _update_tracking_google_sheet(self, entries):
        folder_url = self.gdrive_upload_service.get_employee_root_url(
            str(self.unipe_employee_id))
        sheet_rows = [self.common_columns + entry + [folder_url]
                      for entry in entries]
        self.google_sheets_service.append_entries(sheet_rows)
