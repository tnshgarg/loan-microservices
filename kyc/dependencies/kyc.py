
import logging
from kyc.config import Config
from services.kyc.gridlines import GridlinesApi
from services.storage.sheets.google_sheets import GoogleSheetsService
from services.storage.uploads.drive_upload_service import DriveUploadService
from services.storage.uploads.s3_upload_service import S3UploadService
from cachetools import cached, TTLCache

GRIDLINES_API = None


def gridlines_api():
    global GRIDLINES_API
    if GRIDLINES_API is None:
        GRIDLINES_API = GridlinesApi(
            logger=logging.getLogger("gridlines_service"))
    return GRIDLINES_API


@cached(cache=TTLCache(maxsize=32, ttl=300))
def gdrive_upload_service():
    return DriveUploadService()


@cached(cache=TTLCache(maxsize=32, ttl=300))
def loans_gdrive_upload_service():
    return DriveUploadService(base_folder_id=Config.LOANS_GDRIVE_BASE_FOLDER_ID)


@cached(cache=TTLCache(maxsize=32, ttl=300))
def s3_upload_service():
    return S3UploadService(Config.BUCKET)


@cached(cache=TTLCache(maxsize=32, ttl=300))
def google_sheets_service():
    return GoogleSheetsService()
