

import bson
from dal.models.auth_video_otp import VideoOTP
from dal.models.offer import Offers
from dal.utils import db_txn
from kyc_service.services.storage.sheets.google_sheets import GoogleSheetsService
from kyc_service.services.storage.uploads.drive_upload_service import DriveUploadService
from kyc_service.services.storage.uploads.media_upload_service import MediaUploadService
from kyc_service.services.storage.uploads.s3_upload_service import S3UploadService
from random import randint


class VideoOtpService(MediaUploadService):

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

    @staticmethod
    def generate_code():
        return str(randint(100000, 999999))

    @db_txn
    def generate_otp(self, offer_id):
        VideoOTP.update(
            {
                "unipeEmployeeId": self.unipe_employee_id,
                "status": VideoOTP.Stage.PENDING
            },
            {
                "$set": {
                    "status": VideoOTP.Stage.EXPIRED
                }
            }
        )
        generated_otp = self.generate_code()
        VideoOTP.insert_one({
            "unipeEmployeeId": self.unipe_employee_id,
            "status": VideoOTP.Stage.PENDING,
            "offerId": offer_id,
            "otp": generated_otp
        })

        return generated_otp

    @db_txn
    def verify_otp(self, uploaded_video, offer_id, sales_user_id):
        video_otp_doc = VideoOTP.find_one({
            "unipeEmployeeId": self.unipe_employee_id,
            "status": VideoOTP.Stage.PENDING,
            "offerId": offer_id,
        })
        otp = video_otp_doc["otp"]
        web_url = self._upload_media(
            uploaded_video, f"video_otp_{offer_id}_[{otp}]")
        VideoOTP.update_one({
            "unipeEmployeeId": self.unipe_employee_id,
            "status": VideoOTP.Stage.PENDING,
            "offerId": offer_id,
        }, {"$set": {
            "status": VideoOTP.Stage.SUBMITTED,
            "link": web_url
        }})
        Offers.update_one({
            "_id": offer_id
        }, {"$set": {
            "verifier_sales_id": sales_user_id,
            "videoOtpLink": web_url,
            "kycFolder": self.gdrive_upload_service.get_employee_root_url(str(self.unipe_employee_id))
        }})
        self._update_tracking_google_sheet([
            [f'video_otp_{offer_id}', 'SUCCESS', web_url],
        ])
        return web_url
