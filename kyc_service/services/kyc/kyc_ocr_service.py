
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
from kyc_service.dependencies.kyc import gdrive_upload_service, gridlines_api, s3_upload_service
from kyc_service.services.kyc.gridlines import GridlinesApi
from kyc_service.services.storage.sheets.google_sheets import GoogleSheetsService
from kyc_service.services.storage.uploads.drive_upload_service import DriveUploadService
from kyc_service.services.storage.uploads.s3_upload_service import S3UploadService


class KYCOCRService:

    def __init__(self,
                 unipe_employee_id: bson.ObjectId,
                 sales_user_id: bson.ObjectId,
                 gridlines_api: GridlinesApi,
                 gdrive_upload_service: DriveUploadService,
                 s3_upload_service: S3UploadService,
                 google_sheets_service: GoogleSheetsService
                 ) -> None:
        self.unipe_employee_id = unipe_employee_id
        self.sales_user_id = sales_user_id
        self.gdrive_upload_service = gdrive_upload_service
        self.s3_upload_service = s3_upload_service
        self.gridlines_api = gridlines_api
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

    def _upload_image(self, form_file, filename):
        file_extension = self._parse_extension(form_file.content_type)
        drive_upload_response = self.gdrive_upload_service.upload_file(
            str(self.unipe_employee_id),
            f"{self.ts_prefix}_{filename}.{file_extension}",
            mime_type=form_file.content_type,
            fd=form_file.file,
            description=f"Unipe Employee Id: {self.unipe_employee_id} \n Sales User: {self.sales_user_id}"
        )
        self.s3_upload_service.upload(
            key=f"{self.unipe_employee_id}/{self.ts_prefix}_{filename}.{file_extension}",
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
            key=f"{self.unipe_employee_id}/{self.ts_prefix}_{filename}.txt",
            fd=dummy_file
        )
        return drive_upload_response["webViewLink"]

    def _update_tracking_google_sheet(self, entries):
        folder_url = self.gdrive_upload_service.get_employee_root_url(
            str(self.unipe_employee_id))
        sheet_rows = [self.common_columns + entry + [folder_url]
                      for entry in entries]
        self.google_sheets_service.append_entries(sheet_rows)

    @db_txn
    def perform_aadhaar_kyc(self, front_image, back_image, signature):
        aadhar_front_drive_url = self._upload_image(
            form_file=front_image,
            filename="aadhaar_front"
        )
        aadhar_back_drive_url = self._upload_image(
            form_file=back_image,
            filename="aadhaar_back"
        )
        signature_drive_url = self._upload_image(
            form_file=signature,
            filename="signature_employee"
        )
        front_ocr_status, front_ocr = self.gridlines_api.aadhaar_ocr(
            front_image.file)
        back_ocr_status, back_ocr = self.gridlines_api.aadhaar_ocr(
            back_image.file)
        front_ocr_doc = front_ocr.get("data", {}).get(
            "ocr_data", {}).get("document", {})
        if "year_of_birth" in front_ocr_doc:
            front_ocr_doc["date_of_birth"] = front_ocr_doc["year_of_birth"] + "-XX-XX"

        back_ocr_doc = back_ocr.get("data", {}).get(
            "ocr_data", {}).get("document", {})
        self._upload_text(json.dumps(front_ocr, indent=4),
                          "gridlines_ocr_aadhaar_front")
        self._upload_text(json.dumps(back_ocr, indent=4),
                          "gridlines_ocr_aadhaar_back")
        front_ocr_doc["address"] = back_ocr_doc["address"]

        self._update_tracking_google_sheet([
            ['aadhaar_front', 'SUCCESS', aadhar_front_drive_url],
            ['aadhaar_back', 'SUCCESS', aadhar_back_drive_url],
            ['signature', 'SUCCESS', signature_drive_url],
        ])
        GovernmentIds.update_one(
            filter_={
                "pId": self.unipe_employee_id,
                "type": "aadhaar",
                "uType": "employee"
            },
            update={
                "$set": {
                    "sales_user_id": self.sales_user_id,
                    "number": front_ocr_doc["document_id"],
                    "data": front_ocr_doc,
                    "verifyStatus": "INPROGRESS_OTP",
                    "verifyMsg": "OCR Completed",
                    "verifyTimestamp": front_ocr.get("timestamp")
                }
            }, upsert=True
        )

    @db_txn
    def perform_user_verification(self, user_photo, user_idphoto):
        user_photo_drive_url = self._upload_image(
            form_file=user_photo,
            filename="user_photo"
        )
        user_id_photo_drive_url = self._upload_image(
            form_file=user_idphoto,
            filename="user_idphoto"
        )
        self._update_tracking_google_sheet([
            ['profile_user', 'SUCCESS', user_photo_drive_url],
            ['profile_idcard', 'SUCCESS', user_id_photo_drive_url],
        ])
        user_photo.file.seek(0)
        GovernmentIds.update_one(
            filter_={
                "pId": self.unipe_employee_id,
                "type": "aadhaar",
                "uType": "employee"
            },
            update={
                "$set": {
                    "data.photo_base64": b64encode(user_photo.file.read()).decode(),
                    "verifyStatus": "INPROGRESS_CONFIRMATION",
                    "verifyMsg": "User Photos Uploaded",
                }
            }, upsert=True
        )
