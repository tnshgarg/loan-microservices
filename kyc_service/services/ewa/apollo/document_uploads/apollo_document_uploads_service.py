

from dataclasses import dataclass
from bson import ObjectId
import requests
from kyc_service.services.ewa.apollo.apollo_api import ApolloAPI
from kyc_service.services.ewa.apollo.constants import ApolloDocument, ApolloDocumentLevel, ApolloPartnerTag
from kyc_service.services.ewa.ewa_constants import LoanProvider
from kyc_service.services.ewa.ewa_document_upload_service import EwaDocumentUploadService


@dataclass
class ApolloUploadResponse:
    drive_link: str
    s3_path: str
    apollo_key: str


class ApolloDocumentUploadsService(EwaDocumentUploadService):

    def __init__(self, unipe_employee_id: ObjectId, loan_application_id: ObjectId, offer_id: ObjectId, partner_loan_id: str) -> None:
        super().__init__(
            unipe_employee_id,
            loan_application_id,
            offer_id,
            provider=LoanProvider.APOLLO
        )
        self.partner_loan_id = partner_loan_id
        self.apollo_api = ApolloAPI()

    def _upload_media(self, fd, apollo_document: ApolloDocument, partner_tag: ApolloPartnerTag) -> ApolloUploadResponse:
        drive_link, s3_key = super()._upload_media(
            fd,
            apollo_document.filename,
            apollo_document.extension,
            apollo_document.mime_type
        )
        document_link = self.apollo_api.get_document_upload_link(
            partner_tag=partner_tag,
            partner_loan_id=self.partner_loan_id,
            document_key=apollo_document.upload_key
        )
        fd.seek(0)
        upload_res = requests.put(
            url=document_link["signed_url"],
            data=fd,
            headers={
                "Content-Type": apollo_document.mime_type,
                "Slug": apollo_document.upload_key
            }
        )
        if upload_res.status_code != 200:
            raise Exception("Document Upload Failed")
        return ApolloUploadResponse(
            drive_link,
            s3_key,
            document_link["path"]
        )
