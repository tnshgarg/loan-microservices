
from bson import ObjectId
from fastapi import HTTPException
from kyc.dependencies.ewa import ewa_gdrive_upload_service, ewa_google_sheets_service, ewa_s3_upload_service
from services.storage.uploads.media_upload_service import MediaUploadService


class EwaDocumentUploadService(MediaUploadService):

    def __init__(self,
                 unipe_employee_id: ObjectId,
                 loan_application_id: ObjectId,
                 offer_id: ObjectId,
                 provider: str
                 ) -> None:
        super().__init__(
            unipe_employee_id,
            None,
            ewa_gdrive_upload_service(),
            ewa_s3_upload_service(),
            ewa_google_sheets_service()
        )
        self.loan_application_id = loan_application_id
        self.offer_id = offer_id
        self.provider = provider

    @property
    def folder_description(self):
        return (f"Unipe Employee Id: {self.unipe_employee_id} \n"
                f"Offer Id: {self.offer_id} \n"
                f"Provider: {self.provider} \n"
                f"LoanApplicationId: {self.loan_application_id}\n"
                )

    def _upload_media(self, fd, filename, extension, mime):
        idx_filename = f"{self.ts_prefix}_{filename}.{extension}"
        drive_upload_response = self.gdrive_upload_service.upload_file(
            child_folder_name=str(self.offer_id),
            name=idx_filename,
            mime_type=mime,
            fd=fd,
            description=self.folder_description
        )

        s3_key = f"{self.provider}/{self.loan_application_id}/{self.offer_id}/{idx_filename}"
        status, asset_url = self.s3_upload_service.upload(
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

    def _upload_text(self, text, filename):
        raise HTTPException(
            status_code=501,
            detail="Operation not allowed"
        )

    def _update_tracking_google_sheet(self, entries):
        folder_url = self.gdrive_upload_service.get_child_folder_root_url(
            str(self.unipe_employee_id))
        sheet_rows = [self.common_columns + entry + [folder_url]
                      for entry in entries]
        self.google_sheets_service.append_entries(sheet_rows)
