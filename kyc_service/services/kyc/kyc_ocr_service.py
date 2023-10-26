
from base64 import b64encode
from datetime import datetime
import io
import json
from typing import Annotated
import bson
from fastapi import Depends, HTTPException
from dal.models.employees import Employee
from dal.models.encrypted_government_ids import EncryptedGovernmentIds
from dal.models.government_ids import GovernmentIds
from dal.utils import db_txn
from kyc_service.config import Config
from kyc_service.dependencies.kyc import gdrive_upload_service, gridlines_api, s3_upload_service
from kyc_service.services.kyc.gridlines import GridlinesApi
from kyc_service.services.storage.sheets.google_sheets import GoogleSheetsService
from kyc_service.services.storage.uploads.drive_upload_service import DriveUploadService
from kyc_service.services.storage.uploads.media_upload_service import MediaUploadService
from kyc_service.services.storage.uploads.s3_upload_service import S3UploadService


class KYCOCRService(MediaUploadService):

    def __init__(self,
                 unipe_employee_id: bson.ObjectId,
                 sales_user_id: bson.ObjectId,
                 gridlines_api: GridlinesApi,
                 gdrive_upload_service: DriveUploadService,
                 s3_upload_service: S3UploadService,
                 google_sheets_service: GoogleSheetsService
                 ) -> None:
        super().__init__(
            unipe_employee_id,
            sales_user_id,
            gdrive_upload_service,
            s3_upload_service,
            google_sheets_service
        )
        self.gridlines_api = gridlines_api

    @staticmethod
    def validate_aadhaar_doc(aadhaar):
        expected_fields = [
            "document_id",
            "address",
            "name",
            "date_of_birth",
            "gender"
        ]
        return all([aadhaar.get(field) for field in expected_fields])

    @db_txn
    def perform_aadhaar_kyc(self, front_image, back_image, signature):
        aadhar_front_drive_url = self._upload_media(
            form_file=front_image,
            filename="aadhaar_front"
        )
        aadhar_back_drive_url = self._upload_media(
            form_file=back_image,
            filename="aadhaar_back"
        )
        signature_drive_url = self._upload_media(
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
        if front_ocr_status != 200 or back_ocr_status != 200 or front_ocr["data"]["code"] != "1014" or back_ocr["data"]["code"] != "1014":
            raise HTTPException(
                status_code=400,
                detail="Error Reading Aadhaar Details click photo again"
            )
        self._upload_text(json.dumps(front_ocr, indent=4),
                          "gridlines_ocr_aadhaar_front")
        self._upload_text(json.dumps(back_ocr, indent=4),
                          "gridlines_ocr_aadhaar_back")
        front_ocr_doc["address"] = back_ocr_doc["address"]

        if not self.validate_aadhaar_doc(front_ocr_doc):
            raise HTTPException(
                status_code=400,
                detail="Missing fields click photo again"
            )

        self._update_tracking_google_sheet([
            ['aadhaar_front', 'SUCCESS', aadhar_front_drive_url],
            ['aadhaar_back', 'SUCCESS', aadhar_back_drive_url],
            ['signature', 'SUCCESS', signature_drive_url],
        ])
        EncryptedGovernmentIds.update_one(
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
        user_photo_drive_url = self._upload_media(
            form_file=user_photo,
            filename="user_photo"
        )
        user_id_photo_drive_url = self._upload_media(
            form_file=user_idphoto,
            filename="user_idphoto"
        )
        self._update_tracking_google_sheet([
            ['profile_user', 'SUCCESS', user_photo_drive_url],
            ['profile_idcard', 'SUCCESS', user_id_photo_drive_url],
        ])
        user_photo.file.seek(0)
        EncryptedGovernmentIds.update_one(
            filter_={
                "pId": self.unipe_employee_id,
                "type": "aadhaar",
                "uType": "employee"
            },
            update={
                "$set": {
                    "sales_user_id": self.sales_user_id,
                    "data.photo_base64": b64encode(user_photo.file.read()).decode(),
                    "verifyStatus": "INPROGRESS_CONFIRMATION",
                    "verifyMsg": "User Photos Uploaded",
                }
            }, upsert=True
        )
