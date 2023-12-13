
import logging
from kyc.config import Config
from services.employer.uploads.employer_drive_upload_service import EmployerDriveUploadService
from services.storage.sheets.google_sheets import GoogleSheetsService
from services.storage.uploads.s3_upload_service import S3UploadService
from cachetools import cached, TTLCache


@cached(cache=TTLCache(maxsize=32, ttl=300))
def payslip_gdrive_upload_service(employer_id):
    root_employer_service = EmployerDriveUploadService(
        base_folder_id=Config.GDRIVE_PAYSLIP_BASE_FOLDERID)
    employer_folder_id = root_employer_service.get_or_create_child_folder_root(
        employer_id)
    return EmployerDriveUploadService(base_folder_id=employer_folder_id)


@cached(cache=TTLCache(maxsize=32, ttl=300))
def payslip_s3_upload_service():
    return S3UploadService(f"{Config.STAGE}-unipe-employer-salary-slips")


@cached(cache=TTLCache(maxsize=32, ttl=300))
def payslip_google_sheets_service():
    return GoogleSheetsService(sheet_id=Config.PAYSLIP_GOOGLE_SHEET)
