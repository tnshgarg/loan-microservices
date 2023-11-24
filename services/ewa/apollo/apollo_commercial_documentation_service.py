

import io
import json
from bson import ObjectId
import requests
from dal.models.disbursement import Disbursements
from dal.models.employer import Employer
from dal.models.government_ids import GovernmentIds
from dal.models.offer import Offers
from kyc.config import Config
from services.ewa.apollo.apollo_documentation_service import ApolloDocumentsService
from services.ewa.apollo.constants import ApolloDocumentList, ApolloPartnerTag
from services.ewa.apollo.document_handling.addendum_service import ApolloAddendumService
from services.ewa.apollo.document_handling.commercial_loan_agreement_service import ApolloCommercialLoanAgreementService
from services.ewa.apollo.document_handling.directors_list_service import DirectorsListService
from services.ewa.apollo.document_handling.document_signing_service import DocumentSigningService
from services.ewa.apollo.loan_application_api import ApolloLoanApplicationHook
from services.storage.uploads.s3_upload_service import S3UploadService


class ApolloCommercialDocumentsService(ApolloDocumentsService):

    def __init__(self, unipe_employee_id: ObjectId, loan_application_id: ObjectId, offer_id: ObjectId) -> None:
        super().__init__(unipe_employee_id, loan_application_id, offer_id)
        self.employer = Employer.find_one({
            "commercialLoanDetails.keyPromoter": unipe_employee_id
        })
        self.employer_s3_service = S3UploadService(
            bucket=f"{Config.STAGE}-unipe-employer-final"
        )

    def _get_s3_object_fd(self, path):
        download_url = self.employer_s3_service.get_presigned_url(
            path, use_stage=False)
        response = requests.get(download_url)
        return io.BytesIO(response.content)

    def _upload_list_of_directors(self):
        directors_list_service = DirectorsListService(self.employer)
        directors_list_fd = directors_list_service.generate_document()
        self._upload_apollo_document(
            directors_list_fd,
            ApolloDocumentList.LIST_OF_DIRECTORS,
            ApolloPartnerTag.LOC_COMMERCIAL
        )

    def _upload_gst_certificate(self):
        self._upload_apollo_document(
            self._get_s3_object_fd(
                self.employer["document_uploads"]["gst_certificate"]),
            ApolloDocumentList.GST_CERTIFICATE,
            ApolloPartnerTag.LOC_COMMERCIAL
        )

    def _upload_incorporation_certificate(self):
        self._upload_apollo_document(
            self._get_s3_object_fd(
                self.employer["document_uploads"]["incorporation_certificate"]),
            ApolloDocumentList.INCORPORATION_CERTIFICATE,
            ApolloPartnerTag.LOC_COMMERCIAL
        )

    def _upload_bank_statement(self):
        self._upload_apollo_document(
            self._get_s3_object_fd(
                self.employer["document_uploads"]["bank_statement"]),
            ApolloDocumentList.BANK_STATEMENT,
            ApolloPartnerTag.LOC_COMMERCIAL
        )

    def _upload_bureau_report(self):
        self._upload_apollo_document(
            self._get_s3_object_fd(
                self.employer["document_uploads"]["bureau"]),
            ApolloDocumentList.COMMERCIAL_CRIFF,
            ApolloPartnerTag.LOC_COMMERCIAL
        )

    def _upload_company_pan(self):
        company_pan = GovernmentIds.find_one({
            "pId": self.employer["_id"],
            "type": "pan",
            "provider": "karza"
        })
        pan_fd = io.StringIO()
        json.dump(company_pan["karzaResponse"], pan_fd)
        self._upload_apollo_document(
            pan_fd,
            ApolloDocumentList.PAN,
            ApolloPartnerTag.LOC_PERSONAL
        )

    def _generate_agreement(self):
        loan_agreement_service = ApolloCommercialLoanAgreementService(
            self.loan_application)
        loan_agreement_fd = loan_agreement_service.generate_document()
        self._upload_apollo_document(
            loan_agreement_fd,
            ApolloDocumentList.LOAN_AGREEMENT,
            ApolloPartnerTag.LOC_COMMERCIAL
        )
        return loan_agreement_fd

    def _generate_addendum(self):
        addendum_service = ApolloAddendumService(
            self.loan_application, self.offer)
        addendum_fd = addendum_service.generate_document()
        self._upload_apollo_document(
            addendum_fd,
            ApolloDocumentList.ADDENDUM,
            ApolloPartnerTag.DISBURSEMENT_COMMERCIAL
        )
        return addendum_fd

    def upload_loan_documents(self):
        self._upload_list_of_directors()
        self._upload_gst_certificate()
        self._upload_incorporation_certificate()
        self._upload_bank_statement()
        self._upload_bureau_report()
        self._upload_company_pan()
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
                        "Loan Agreement": la_addendum_upload_response.s3_path,
                        "Sanction Letter and KFS": sl_kfs_upload_response.s3_path
                    },
                    "documentation.gdrive": {
                        "la_addendum": la_addendum_upload_response.drive_link,
                        "sl_kfs": sl_kfs_upload_response.drive_link
                    }
                }
            }
        )

    def upload_signed_loc_documents(self):
        signing_service = DocumentSigningService(self.offer)
        sl_kfs_url = self.s3_upload_service.get_presigned_url(
            self.loan_application["uploads"]["loc"]["s3"][ApolloDocumentList.SL_KFS.name],
            use_stage=False)
        print("s3_url", sl_kfs_url)
        signed_sl_kfs_fd = signing_service.sign_pdf(
            self.get_pdf_file_http(sl_kfs_url))
        self._upload_apollo_document(
            fd=signed_sl_kfs_fd,
            apollo_document=ApolloDocumentList.SIGNED_SL_KFS,
            partner_tag=ApolloPartnerTag.LOC_COMMERCIAL
        )
        loan_agreement_url = self.s3_upload_service.get_presigned_url(
            self.loan_application["uploads"]["loc"]["s3"][ApolloDocumentList.LOAN_AGREEMENT.name],
            use_stage=False)
        print("s3_url", loan_agreement_url)
        signed_loan_agreement_fd = signing_service.sign_pdf(
            self.get_pdf_file_http(loan_agreement_url))
        self._upload_apollo_document(
            fd=signed_loan_agreement_fd,
            apollo_document=ApolloDocumentList.SIGNED_LOAN_AGREEMENT,
            partner_tag=ApolloPartnerTag.LOC_COMMERCIAL
        )

    def upload_signed_addendum(self):
        signing_service = DocumentSigningService(self.offer)
        addendum_url = self.s3_upload_service.get_presigned_url(
            self.loan_application["uploads"]["disbursements"][
                f"{self.offer_id}"]["s3"][ApolloDocumentList.ADDENDUM.name],
            use_stage=False)

        signed_addendup_fd = signing_service.sign_pdf(
            self.get_pdf_file_http(addendum_url))
        self._upload_apollo_document(
            fd=signed_addendup_fd,
            apollo_document=ApolloDocumentList.SIGNED_ADDENDUM,
            partner_tag=ApolloPartnerTag.DISBURSEMENT_COMMERCIAL
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
