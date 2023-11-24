from dal.models.employer import Employer
from services.storage.uploads.drive_upload_service import DriveUploadService

GDRIVE_FOLDER_MIMETYPE = "application/vnd.google-apps.folder"
GDRIVE_FOLDER_URL_TEMPLATE = "https://drive.google.com/drive/folders/{folder_id}"
ROOT_FOLDER_DESCRIPTION_TEMPLATE = """
Company: {companyName}
Type: {companyType}
"""


class EmployerDriveUploadService(DriveUploadService):
    def get_description(self, child_folder_name: str):
        try:
            employer_doc = Employer.find_one({"_id": child_folder_name})
            if employer_doc is None:
                self.logger.warning(
                    f"No employer found with ID: {child_folder_name}")
                return ""
            return ROOT_FOLDER_DESCRIPTION_TEMPLATE.format(**employer_doc)
        except Exception as e:
            self.logger.error(f"Error in get_description: {str(e)}")
            return ""
