
from services.employer.uploads.employer_upload_service import EmployerUploadService


class EmployerLoanDocumentsUploadService(EmployerUploadService):

    def _add_to_db(self, doc_type, drive_url, s3_path):
        self.update_employer({
            f"document_uploads.{doc_type}": s3_path[1:],
            f"drive_links.{doc_type}": drive_url,
        })
