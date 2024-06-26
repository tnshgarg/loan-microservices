
import logging
from kyc.config import Config
from services.kyc.gridlines import GridlinesApi
from services.storage.sheets.google_sheets import GoogleSheetsService
from services.storage.uploads.drive_upload_service import DriveUploadService
from services.storage.uploads.s3_upload_service import S3UploadService
from cachetools import cached, TTLCache


@cached(cache=TTLCache(maxsize=32, ttl=300))
def ewa_gdrive_upload_service():
    return DriveUploadService(base_folder_id=Config.GDRIVE_LOANS_BASE_FOLDERID)


@cached(cache=TTLCache(maxsize=32, ttl=300))
def ewa_s3_upload_service():
    return S3UploadService(Config.LOANS_BUCKET)


@cached(cache=TTLCache(maxsize=32, ttl=300))
def ewa_google_sheets_service():
    return GoogleSheetsService(sheet_id=Config.LOANS_GOOGLE_SHEET)
