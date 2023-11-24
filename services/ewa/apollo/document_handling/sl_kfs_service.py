
from io import BytesIO

import requests

from services.ewa.apollo.constants import ApolloDocumentList
from services.storage.uploads.s3_upload_service import S3UploadService


class ApolloSLKFSService:

    def __init__(self, loan_application, s3_service: S3UploadService) -> None:
        self.loan_application = loan_application
        self.s3_service = s3_service

    def generate_document(self) -> BytesIO:
        download_url = None
        s3_key = self.loan_application["uploads"]["loc"]["s3"].get(
            ApolloDocumentList.SL_KFS.name)

        if s3_key is not None:
            download_url = self.s3_service.get_presigned_url(
                s3_key, use_stage=False)
        else:
            download_url = self.loan_application["data"]["documentsDownloadUrl"]

        response = requests.get(download_url)
        return BytesIO(response.content)
