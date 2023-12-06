import bson
from fastapi import HTTPException
from dal.models.payslips import Payslips
from services.storage.uploads.media_upload_service import MediaUploadService
from kyc.dependencies.admin import admin_gdrive_upload_service, admin_google_sheets_service, admin_s3_upload_service


class PayslipUploadService(MediaUploadService):
    def __init__(self,
                 employment_id: bson.ObjectId,
                 ) -> None:
        super().__init__(
            None,
            employment_id,
            admin_gdrive_upload_service(),
            admin_s3_upload_service(),
            admin_google_sheets_service()
        )
        self.employment_id = employment_id

    def upload_document(self,  file_name, form_file, content_type):
        drive_url, s3_key = self._upload_media(
            form_file=form_file,
            filename=file_name,
            content_type=content_type
        )
        self._add_to_db(drive_url, s3_key)
        return drive_url

    def _upload_media(self, form_file, filename, content_type, s3_prefix="admin_upload_service"):
        file_extension = self._parse_extension(content_type)
        idx_filename = f"{self.ts_prefix}_{filename}.{file_extension}"
        drive_upload_response = self.gdrive_upload_service.upload_file(
            child_folder_name=str(self.employment_id),
            name=idx_filename,
            mime_type=content_type,
            fd=form_file,
            description=f"Employer Id: {self.employment_id}"
        )

        s3_key = f"{s3_prefix}/{self.employment_id}/{idx_filename}"
        status, _ = self.s3_upload_service.upload(
            key=s3_key,
            fd=form_file
        )
        if status is False:
            raise HTTPException(
                status_code=500,
                detail="s3 upload failure"
            )
        return drive_upload_response["webViewLink"], s3_key

    def update_employer(self, update):
        return Payslips.update_one(
            {"_id": self.employment_id},
            {
                "$set": update
            }, upsert=False
        )

    def _add_to_db(self, drive_url, s3_path):
        self.update_employer({
            f"documents.drive": drive_url,
            f"documents.s3": s3_path,
        })
