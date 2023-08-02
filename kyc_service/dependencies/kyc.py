
import logging
from kyc_service.config import Config
from kyc_service.services.kyc.gridlines import GridlinesApi
from kyc_service.services.storage.sheets.google_sheets import GoogleSheetsService
from kyc_service.services.storage.uploads.drive_upload_service import DriveUploadService
from kyc_service.services.storage.uploads.s3_upload_service import S3UploadService


GRIDLINES_API = None
GDRIVE_UPLOAD_SERVICE = None
S3_UPLOAD_SERVICE = None
GOOLGE_SHEETS_SERVICE = None


def gridlines_api():
    global GRIDLINES_API
    if GRIDLINES_API is None:
        GRIDLINES_API = GridlinesApi(
            logger=logging.getLogger("gridlines_service"))
    return GRIDLINES_API


def gdrive_upload_service():
    global GDRIVE_UPLOAD_SERVICE
    if GDRIVE_UPLOAD_SERVICE is None:
        GDRIVE_UPLOAD_SERVICE = DriveUploadService()
    return GDRIVE_UPLOAD_SERVICE


def s3_upload_service():
    global S3_UPLOAD_SERVICE
    if S3_UPLOAD_SERVICE is None:
        S3_UPLOAD_SERVICE = S3UploadService(Config.BUCKET)
    return S3_UPLOAD_SERVICE


def google_sheets_service():
    global GOOLGE_SHEETS_SERVICE
    if GOOLGE_SHEETS_SERVICE is None:
        GOOLGE_SHEETS_SERVICE = GoogleSheetsService()
    return GOOLGE_SHEETS_SERVICE
