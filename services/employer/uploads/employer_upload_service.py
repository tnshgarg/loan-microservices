import functools
import bson
from fastapi import HTTPException
from dal.models.employer import Employer
from dal.utils import db_txn
from services.storage.uploads.media_upload_service import MediaUploadService
from kyc.dependencies.admin import admin_gdrive_upload_service, admin_google_sheets_service, admin_s3_upload_service
from services.storage.uploads.drive_upload_service import DriveUploadService
from starlette.background import BackgroundTasks


class EmployerUploadService(MediaUploadService):
    def __init__(self,
                 employer_id: bson.ObjectId,
                 ) -> None:
        super().__init__(
            None,
            employer_id,
            admin_gdrive_upload_service(),
            admin_s3_upload_service(),
            admin_google_sheets_service()
        )
        self.employer_id = employer_id

    def upload_document(self,  document_type, form_file, content_type):
        drive_url, s3_key = self._upload_media(
            form_file=form_file,
            filename=f"{document_type}_document",
            content_type=content_type  # Assuming all documents are PDFs
        )
        self._add_to_db(document_type, drive_url, s3_key)
        return drive_url

    def _upload_media(self, form_file, filename, content_type, s3_prefix=""):
        file_extension = self._parse_extension(content_type)
        idx_filename = f"{self.ts_prefix}_{filename}.{file_extension}"
        drive_upload_response = self.gdrive_upload_service.upload_file(
            child_folder_name=str(self.employer_id),
            name=idx_filename,
            mime_type=content_type,
            fd=form_file,
            description=f"Employer Id: {self.employer_id}"
        )

        s3_key = f"/{self.employer_id}/uploads/{idx_filename}"
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
        return Employer.update_one(
            {"_id": self.employer_id},
            {
                "$set": update
            }, upsert=False
        )

    def _add_to_db(self, doc_type, drive_url, s3_path):
        self.update_employer({
            f"documents.drive.{doc_type}": drive_url,
            f"documents.s3.{doc_type}": s3_path,
        })

# Integration with BackgroundTasks


def upload_employer_documents(background_tasks: BackgroundTasks, employer_upload_service: EmployerUploadService, documents):
    background_tasks.add_task(
        employer_upload_service.upload_documents, documents
    )
