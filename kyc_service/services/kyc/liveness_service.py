import bson
import requests
import base64
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

    @db_txn
    def perform_liveness_check(self, liveness_picture):
        liveness_pic_drive_url = self._upload_media(
            form_file=liveness_picture,
            filename="liveness_picture"
        )

        print("liveness drive url: ", liveness_pic_drive_url)

        liveness_check_result = self._karza_liveness_check(liveness_picture, liveness_pic_drive_url)
        print("LiveNess: ", liveness_check_result)
        # if liveness_check_result["result"]["isLive"]:
        #     print("all success")
        #     # self._update_database_status("SUCCESS")
        # else:
        #     print("all wrong")
        #     # self._update_database_status("FAILURE")

        return liveness_check_result

    def _karza_liveness_check(self, liveness_picture, liveness_pic_drive_url):
        endpoint_url = "https://testapi.karza.in/v3/liveness-detection"
        headers = {
            "x-karza-key": Config.KARZA_API_KEY
        }
        # payload = {
        #     "file": (liveness_picture.filename, liveness_picture.file, liveness_picture.content_type),
        #     "faceSelectionMode": "",
        #     "clientData": {
        #         "caseId": "123456" 
        #     }
        # }
        liveness_picture.file.seek(0)
        image_data = liveness_picture.file.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')


        # Prepare the JSON payload
        payload = {
            # "url": liveness_pic_drive_url,
            "url": "https://d22ss3ef1t9wna.cloudfront.net/ad-hoc/2023_08_07_12_22_user_photo.jpeg",
            # "clientData": {
            #     "caseId": "12"
            # }
        }

        # multipart_body = self._generate_multipart_body(liveness_picture)

        response = requests.post(endpoint_url, headers=headers, json=payload)

        print("Response: ", response.json())

        if response.status_code == 200:
            response_data = response.json()
            print("Response Data: ", response_data)
            return response_data  
        else:
            return "FAILURE"

    def _update_database_status(self, status):
        # Update the database with the liveness check status
        pass

    def _generate_multipart_body(self, liveness_video):
        # Create the boundary for multipart/form-data
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'

        # Construct the multipart/form-data request body
        body = []
        body.append('--' + boundary)
        body.append(f'Content-Disposition: form-data; name="file"; filename="{liveness_video.filename}"')
        body.append(f'Content-Type: {liveness_video.content_type}')
        body.append('')  # Blank line to separate headers and content
        body.append(liveness_video.file.read().decode('utf-8'))  # Read the file content and decode it as a string
        body.append('--' + boundary + '--')  # End boundary

        # Join the body parts with CRLF (Carriage Return Line Feed)
        multipart_body = '\r\n'.join(body)

        return multipart_body

