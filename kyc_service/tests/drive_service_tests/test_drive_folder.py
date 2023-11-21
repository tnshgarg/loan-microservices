
import os
from dal.models.db_manager import DBManager
from kyc_service.services.storage.uploads.drive_upload_service import DriveUploadService


def test_drive_folder_create(mocker):
    drive_upload_service = DriveUploadService(base_folder_id=os.getenv(
        "GDRIVE_BASE_FOLDER_ID_TESTS"))
    drive_upload_service.create_employee_root("test_employee_id")


def test_drive_idempotent_folder_create(mocker):
    DBManager.init('dev')
    drive_upload_service = DriveUploadService(base_folder_id=os.getenv(
        "GDRIVE_BASE_FOLDER_ID_TESTS"))
    drive_upload_service.get_or_create_employee_root(
        "6377939e89f886a21c410b1c")
