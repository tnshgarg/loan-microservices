

import io
from bson import ObjectId
import requests
from dal.models.disbursement import Disbursements
from dal.models.encrypted_government_ids import EncryptedGovernmentIds
from dal.models.government_ids import GovernmentIds
from dal.models.loan_applications import LoanApplications
from dal.models.offer import Offers
from services.ewa.apollo.constants import ApolloDocument, ApolloDocumentList, ApolloPartnerTag
from services.ewa.apollo.document_handling.addendum_service import ApolloAddendumService
from services.ewa.apollo.document_handling.apollo_document_uploads_service import ApolloDocumentUploadsService, ApolloUploadResponse
from services.ewa.apollo.document_handling.document_signing_service import DocumentSigningService
from services.ewa.apollo.document_handling.karza_aadhaar_service import AadhaarZipService
from services.ewa.apollo.document_handling.liveness_check_service import LivenessCheckService
from services.ewa.apollo.document_handling.loan_agreement_service import ApolloLoanAgreementService
from services.ewa.apollo.document_handling.pan_document_service import PANStatusCheckService
from services.ewa.apollo.document_handling.salary_slip_service import SalarySlipService
from services.ewa.apollo.document_handling.sl_kfs_service import ApolloSLKFSService
from services.ewa.apollo.loan_application_api import ApolloLoanApplicationHook
from services.storage.uploads.pdf_service import PDFService


class ApolloDocumentsService(ApolloDocumentUploadsService):

    def __init__(self, unipe_employee_id: ObjectId, loan_application_id: ObjectId, offer_id: ObjectId) -> None:
        self.loan_application = LoanApplications.find_one(
            {"_id": loan_application_id}
        )
        self.offer = Offers.find_one(
            {"_id": offer_id}
        )
        self.apollo_loan_application_hook = ApolloLoanApplicationHook(
            unipe_employee_id,
            offer_id
        )
        self.current_disbursement_id = self.loan_application["data"].get(
            "nextDisbursementLoanId")
        super().__init__(
            unipe_employee_id,
            loan_application_id,
            offer_id,
            self.loan_application["externalLoanId"]
        )

    def _add_file_to_application(self, document: ApolloDocument, upload_response: ApolloUploadResponse):

        if upload_response.partner_tag in [ApolloPartnerTag.LOC_PERSONAL, ApolloPartnerTag.LOC_COMMERCIAL]:
            update = {
                f"uploads.loc.s3.{document.name}": upload_response.s3_path,
                f"uploads.loc.drive.{document.name}": upload_response.drive_link
            }
            if upload_response.apollo_key is not None:
                update[f"data.documentUrls.loc.{document.name}"] = upload_response.apollo_key
            LoanApplications.update_one(
                {"_id": self.loan_application_id},
                {
                    "$set": update
                }
            )
        else:
            LoanApplications.update_one(
                {"_id": self.loan_application_id},
                {
                    "$set": {
                        f"data.documentUrls.disbursements.{self.current_disbursement_id}.{document.name}": upload_response.apollo_key,
                        f"uploads.disbursements.{self.offer_id}.s3.{document.name}": upload_response.s3_path,
                        f"uploads.disbursements.{self.offer_id}.drive.{document.name}": upload_response.drive_link
                    }
                }
            )

    def _upload_apollo_document(self, fd, apollo_document, partner_tag):
        if not fd:
            raise Exception(
                f"Error in fetching File Descriptor for {apollo_document.name}")
        fd.seek(0)
        loan_id = None
        if partner_tag in [ApolloPartnerTag.DISBURSEMENT_PERSONAL, ApolloPartnerTag.DISBURSEMENT_COMMERCIAL]:
            loan_id = self.current_disbursement_id
        document_upload_response = self._upload_media(
            fd=fd,
            apollo_document=apollo_document,
            partner_tag=partner_tag,
            loan_id=loan_id
        )
        self._add_file_to_application(
            apollo_document,
            document_upload_response
        )
        return document_upload_response

    def _upload_salary_slip(self):
        salary_slip_fd = SalarySlipService(
            unipe_employee_id=self.unipe_employee_id,
            employer_id=self.offer["employerId"]
        ).generate_document()
        self._upload_apollo_document(
            salary_slip_fd,
            ApolloDocumentList.SALARY_SLIP,
            ApolloPartnerTag.LOC_PERSONAL
        )

    def _upload_aadhaar(self):
        aadhaar_service = AadhaarZipService(self.unipe_employee_id)
        aadhaar_fd = aadhaar_service.generate_document()
        self._upload_apollo_document(
            aadhaar_fd,
            ApolloDocumentList.AADHAAR,
            ApolloPartnerTag.LOC_PERSONAL
        )

    def _upload_pan_status(self):
        pan_service = PANStatusCheckService(self.unipe_employee_id)
        pan_status_fd = pan_service.generate_document()
        self._upload_apollo_document(
            pan_status_fd,
            ApolloDocumentList.PAN,
            ApolloPartnerTag.LOC_PERSONAL
        )

    def _upload_liveness_check(self, partner_tag=ApolloPartnerTag.LOC_PERSONAL):
        liveness_check_service = LivenessCheckService(self.unipe_employee_id)
        liveness_check_fd = liveness_check_service.generate_document()
        self._upload_apollo_document(
            liveness_check_fd,
            ApolloDocumentList.LIVENESS_CHECK,
            partner_tag
        )
        selfie_fd = liveness_check_service.get_selfie()
        self._upload_apollo_document(
            selfie_fd,
            ApolloDocumentList.SELFIE,
            partner_tag
        )

    def _download_sl_kfs(self):
        sl_kfs_service = ApolloSLKFSService(
            self.loan_application,
            self.s3_upload_service
        )
        sl_kfs_fd = sl_kfs_service.generate_document()
        return self._upload_apollo_document(
            sl_kfs_fd,
            ApolloDocumentList.SL_KFS,
            ApolloPartnerTag.LOC_PERSONAL
        )

    def _generate_agreement(self):
        loan_agreement_service = ApolloLoanAgreementService(
            self.loan_application)
        loan_agreement_fd = loan_agreement_service.generate_document()
        self._upload_apollo_document(
            loan_agreement_fd,
            ApolloDocumentList.LOAN_AGREEMENT,
            ApolloPartnerTag.LOC_PERSONAL
        )
        return loan_agreement_fd

    def _generate_addendum(self):
        addendum_service = ApolloAddendumService(
            self.loan_application, self.offer)
        addendum_fd = addendum_service.generate_document()
        self._upload_apollo_document(
            addendum_fd,
            ApolloDocumentList.ADDENDUM,
            ApolloPartnerTag.DISBURSEMENT_PERSONAL
        )
        return addendum_fd

    def _upload_combined_agreement_addendum(self, loan_agreement_fd, addendum_fd):
        loan_agreement_fd.seek(0)
        addendum_fd.seek(0)
        combined_pdf_fd = PDFService.combine_pdfs(
            [loan_agreement_fd, addendum_fd])
        return self._upload_apollo_document(
            combined_pdf_fd,
            ApolloDocumentList.COMBINED_LA_ADDENDUM,
            ApolloPartnerTag.DISBURSEMENT_PERSONAL
        )

    def upload_loan_documents(self):
        self._upload_salary_slip()
        self._upload_aadhaar()
        self._upload_pan_status()
        self._upload_liveness_check()
        self.apollo_loan_application_hook.post_event(
            action=ApolloLoanApplicationHook.Action.LOC,
            status=ApolloLoanApplicationHook.Status.DOCUMENTS_UPLOADED
        )

    def generate_loan_documents(self):
        sl_kfs_upload_response = self._download_sl_kfs()
        agreement_fd = self._generate_agreement()
        addendum_fd = self._generate_addendum()
        la_addendum_upload_response = self._upload_combined_agreement_addendum(
            agreement_fd, addendum_fd)
        Offers.update_one(
            {"_id": self.offer_id},
            {
                "$set": {
                    "stage": "AGREEMENT",
                    "documentation.agreementLinks": {
                        "Loan Agreement and Addendum": la_addendum_upload_response.s3_path,
                        "Sanction Letter and KFS": sl_kfs_upload_response.s3_path
                    }
                }
            }
        )

    def get_pdf_file_http(self, url):
        content = requests.get(url).content
        if content[-4:] == b"EOF\n":
            content = content[:-4]+b"EOF\r\n"
        else:
            content = content+b'%%EOF\r\n'
        fd = io.BytesIO(content)
        return fd

    def upload_signed_loc_documents(self):
        signing_service = DocumentSigningService(self.offer)
        sl_kfs_url = self.s3_upload_service.get_presigned_url(
            self.loan_application["uploads"]["loc"]["s3"][ApolloDocumentList.SL_KFS.name],
            use_stage=False
        )
        print("s3_url", sl_kfs_url)
        sl_kfs_fd = self.get_pdf_file_http(sl_kfs_url)
        signed_sl_kfs_fd = signing_service.sign_pdf(sl_kfs_fd)

        self._upload_apollo_document(
            fd=signed_sl_kfs_fd,
            apollo_document=ApolloDocumentList.SIGNED_SL_KFS,
            partner_tag=ApolloPartnerTag.LOC_PERSONAL
        )
        loan_agreement_url = self.s3_upload_service.get_presigned_url(
            self.loan_application["uploads"]["loc"]["s3"][ApolloDocumentList.LOAN_AGREEMENT.name],
            use_stage=False
        )
        loan_agreement_fd = self.get_pdf_file_http(loan_agreement_url)
        signed_loan_agreement_fd = signing_service.sign_pdf(loan_agreement_fd)
        self._upload_apollo_document(
            fd=signed_loan_agreement_fd,
            apollo_document=ApolloDocumentList.SIGNED_LOAN_AGREEMENT,
            partner_tag=ApolloPartnerTag.LOC_PERSONAL
        )

    def upload_signed_addendum(self):
        signing_service = DocumentSigningService(self.offer)
        addendum_url = self.s3_upload_service.get_presigned_url(
            self.loan_application["uploads"]["disbursements"][
                f"{self.offer_id}"]["s3"][ApolloDocumentList.ADDENDUM.name],
            use_stage=False
        )
        addendum_fd = self.get_pdf_file_http(addendum_url)

        signed_addendup_fd = signing_service.sign_pdf(addendum_fd)
        self._upload_apollo_document(
            fd=signed_addendup_fd,
            apollo_document=ApolloDocumentList.SIGNED_ADDENDUM,
            partner_tag=ApolloPartnerTag.DISBURSEMENT_PERSONAL
        )
        Disbursements.update_one({
            "offerId": self.offer_id
        }, {
            "$set": {
                "externalDisbursementId": self.current_disbursement_id
            }
        })
        self.apollo_loan_application_hook.post_event(
            action=ApolloLoanApplicationHook.Action.DISBURSEMENT,
            status=ApolloLoanApplicationHook.Status.DOCUMENTS_UPLOADED
        )
