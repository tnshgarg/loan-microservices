from http.client import HTTPException
import bson
from dal.models.payslips import Payslips
from services.storage.uploads.media_upload_service import MediaUploadService
from kyc.dependencies.payslip import payslip_gdrive_upload_service, payslip_google_sheets_service, payslip_s3_upload_service

PAYSLIP_S3_BASE_PATH = "payslip_upload_service"


class PayslipUploadService(MediaUploadService):
    def __init__(self,
                 employment_id: bson.ObjectId,
                 ) -> None:
        super().__init__(
            None,
            employment_id,
            payslip_gdrive_upload_service(),
            payslip_s3_upload_service(),
            payslip_google_sheets_service()
        )
        self.employment_id = employment_id

    def _upload_media(self, fd, filename, extension, mime):
        idx_filename = f"{self.ts_prefix}_{filename}.{extension}"
        drive_upload_response = self.gdrive_upload_service.upload_file(
            child_folder_name=str(self.employment_id),
            name=idx_filename,
            mime_type=mime,
            fd=fd,
            description=f"Payslips Data for {self.employment_id}"
        )

        # TODO: Need to create a bucket for Payslips
        s3_key = f"{PAYSLIP_S3_BASE_PATH}/{self.employment_id}/{idx_filename}"
        status, _ = self.s3_upload_service.upload(
            key=s3_key,
            fd=fd,
            use_stage=False
        )
        if status is False:
            raise HTTPException(
                status_code=500,
                detail="s3 upload failure"
            )
        return drive_upload_response["webViewLink"], s3_key

    def _upload_payslip(self, fd, payslip_data):
        if not fd:
            raise Exception(
                f"Error in fetching File Descriptor for {self.employment_id}")
        fd.seek(0)
        drive_link, s3_key = self._upload_media(
            fd,
            filename=f"{self.employment_id}{payslip_data['header']['date']}",
            extension="pdf",
            mime="application/pdf"
        )
        return [drive_link, s3_key]

    def upload_document(self, fd, payslip_data):
        [drive_url, s3_key] = self._upload_payslip(
            fd, payslip_data
        )
        self._add_to_db(drive_url, s3_key)
        return drive_url

    def update_payslips(self, update):
        return Payslips.update_one(
            {"_id": self.employment_id},
            {
                "$set": update
            }, upsert=False
        )

    def _add_to_db(self, drive_url, s3_path):
        self.update_payslips({
            f"documents.drive": drive_url,
            f"documents.s3": s3_path,
        })
