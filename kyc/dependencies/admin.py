
import logging
from kyc.config import Config
from services.employer.uploads.employer_drive_upload_service import EmployerDriveUploadService
from services.storage.sheets.google_sheets import GoogleSheetsService
from services.storage.uploads.s3_upload_service import S3UploadService
from cachetools import cached, TTLCache


@cached(cache=TTLCache(maxsize=32, ttl=300))
def admin_gdrive_upload_service():
    return EmployerDriveUploadService(base_folder_id=Config.GDRIVE_ADMIN_BASE_FOLDERID)


@cached(cache=TTLCache(maxsize=32, ttl=300))
def admin_s3_upload_service():
    return S3UploadService(f"{Config.STAGE}-unipe-employer-final")


@cached(cache=TTLCache(maxsize=32, ttl=300))
def admin_google_sheets_service():
    return GoogleSheetsService(sheet_id=Config.ADMIN_GOOGLE_SHEET)
