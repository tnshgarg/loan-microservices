import json
import bson
import requests
import base64
from dal.models.employees import Employee
from dal.utils import db_txn
from kyc_service.config import Config
from kyc_service.dependencies.kyc import gdrive_upload_service, s3_upload_service
from kyc_service.services.storage.sheets.google_sheets import GoogleSheetsService
from kyc_service.services.storage.uploads.drive_upload_service import DriveUploadService
from kyc_service.services.storage.uploads.media_upload_service import MediaUploadService
from kyc_service.services.storage.uploads.s3_upload_service import S3UploadService


class LivenessService(MediaUploadService):

    def __init__(self,
                 unipe_employee_id: bson.ObjectId,
                 sales_user_id: bson.ObjectId,
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
        self.karza_assets = Config.KARZA
        self.KARZA_API_KEY = self.karza_assets.get("api_key")
        self.KARZA_BASE_URL = self.karza_assets.get("base_url")
        self.unipe_employee_id = unipe_employee_id
        self.sales_user_id = sales_user_id

    @db_txn
    def perform_liveness_check(self, liveness_picture):
        liveness_pic_drive_url, liveness_pic_aws_url = self._upload_media(
            form_file=liveness_picture,
            filename="liveness_picture"
        )

        liveness_check_result = self._karza_liveness_check(
            liveness_pic_aws_url)
        self._update_database_status(
            liveness_check_result, liveness_pic_drive_url, liveness_pic_aws_url)

        if liveness_check_result["statusCode"] == 101:
            return "SUCCESS"
        else:
            return liveness_check_result["statusMessage"]

    def _karza_liveness_check(self, liveness_pic_aws_url):
        endpoint_url = f"{self.KARZA_BASE_URL}/v3/liveness-detection"
        headers = {
            "x-karza-key": self.KARZA_API_KEY
        }
        payload = {
            "url": liveness_pic_aws_url
        }

        response = requests.post(endpoint_url, headers=headers, json=payload)

        print("Response: ", response.json())

        if response.status_code == 200:
            response_data = response.json()
            return response_data
        else:
            return "FAILURE"

    def _update_database_status(self, liveness_check_result, liveness_pic_drive_url, liveness_pic_aws_url):
        Employee.update_one({
            "_id": self.unipe_employee_id
        }, {
            "$set": {
                "liveness": liveness_check_result,
                "profile_pic": {
                    "aws_url":  liveness_pic_aws_url,
                    "drive_url": liveness_pic_drive_url
                }
            }
        }, upsert=True)
