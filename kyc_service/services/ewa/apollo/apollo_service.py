

from bson import ObjectId
from dal.models.encrypted_government_ids import EncryptedGovernmentIds
from dal.models.government_ids import GovernmentIds
from dal.models.loan_applications import LoanApplications
from dal.models.offer import Offers
from kyc_service.services.ewa.apollo.constants import ApolloDocument, ApolloDocumentList, ApolloPartnerTag
from kyc_service.services.ewa.apollo.document_uploads.apollo_document_uploads_service import ApolloDocumentUploadsService, ApolloUploadResponse
from kyc_service.services.ewa.apollo.document_uploads.karza_aadhaar_service import AadhaarZipService
from kyc_service.services.ewa.apollo.document_uploads.liveness_check_service import LivenessCheckService
from kyc_service.services.ewa.apollo.document_uploads.pan_document_service import PANStatusCheckService
from kyc_service.services.ewa.apollo.document_uploads.salary_slip_service import SalarySlipService


class ApolloDocumentsHandler(ApolloDocumentUploadsService):

    def __init__(self, unipe_employee_id: ObjectId, loan_application_id: ObjectId, offer_id: ObjectId) -> None:
        self.loan_application = LoanApplications.find_one(
            {"_id": loan_application_id}
        )
        self.offer = Offers.find_one(
            {"_id": offer_id}
        )
        super().__init__(unipe_employee_id, loan_application_id,
                         offer_id, self.loan_application["data"]["partnerLoanId"])

    def _add_file_to_application(self, document: ApolloDocument, upload_response: ApolloUploadResponse):
        LoanApplications.update_one(
            {"_id": self.loan_application_id},
            {
                "$set": {
                    f"{document.upload_key}": upload_response.apollo_key,
                    f"uploads.s3.{document.upload_key}": upload_response.s3_path,
                    f"uploads.drive.{document.upload_key}": upload_response.drive_link
                }
            }
        )

    def _upload_salary_slip(self):
        salary_slip_fd = SalarySlipService(
            unipe_employee_id=self.unipe_employee_id,
            employer_id=self.offer["employerId"]
        )
        salary_slip_upload_response = self._upload_media(
            fd=salary_slip_fd,
            apollo_document=ApolloDocumentList.SALARY_SLIP,
            partner_tag=ApolloPartnerTag.LOC
        )
        self._add_file_to_application(
            ApolloDocumentList.SALARY_SLIP,
            salary_slip_upload_response
        )

    def _upload_aadhaar(self):
        aadhaar_service = AadhaarZipService(self.unipe_employee_id)
        aadhaar_fd = aadhaar_service.generate_document()
        aadhaar_upload_response = self._upload_media(
            fd=aadhaar_fd,
            apollo_document=ApolloDocumentList.AADHAAR,
            partner_tag=ApolloPartnerTag.LOC
        )
        self._add_file_to_application(
            ApolloDocumentList.AADHAAR,
            aadhaar_upload_response
        )

    def _upload_pan_status(self):
        pan_service = PANStatusCheckService(self.unipe_employee_id)
        pan_status_fd = pan_service.generate_document()
        pan_status_upload_response = self._upload_media(
            fd=pan_status_fd,
            apollo_document=ApolloDocumentList.PAN,
            partner_tag=ApolloPartnerTag.LOC
        )
        self._add_file_to_application(
            ApolloDocumentList.PAN,
            pan_status_upload_response
        )

    def _upload_liveness_check(self):
        liveness_check_service = LivenessCheckService(self.unipe_employee_id)
        liveness_check_fd = liveness_check_service.generate_document()
        liveness_check_upload_response = self._upload_media(
            fd=liveness_check_fd,
            apollo_document=ApolloDocumentList.LIVENESS_CHECK,
            partner_tag=ApolloPartnerTag.LOC
        )
        self._add_file_to_application(
            ApolloDocumentList.LIVENESS_CHECK,
            liveness_check_upload_response
        )

    def upload_loan_documents(self):
        self._upload_salary_slip()
