
from dataclasses import dataclass


class MimeType:
    PDF = "application/pdf"
    ZIP = "application/zip"
    JPEG = "image/jpeg"


@dataclass
class ApolloDocument:
    name: str
    extension: str
    mime_type: str

    @property
    def upload_key(self):
        return f"{self.name}.{self.extension}"


class ApolloPartnerTag:
    LOC = "UEC"
    DISBURSEMENT = "UED"


ApolloDocumentLevel = ApolloPartnerTag


class ApolloDocumentList:
    PAN = ApolloDocument("pan_uidai_xml", "json", MimeType.json)
    AADHAAR = ApolloDocument("aadhar_uidai_xml", "zip", MimeType.ZIP)
    SELFIE = ApolloDocument("selfie", "jpeg", MimeType.JPEG)
    LIVENESS_CHECK = ApolloDocument(
        "liveliness_output", "json", MimeType.json)
    SALARY_SLIP = ApolloDocument("salary_slip", "pdf", MimeType.PDF)
    LOAN_AGREEMENT = ApolloDocument("loan_agreement", "pdf", MimeType.PDF)
    SIGNED_SL_KFS = ApolloDocument(
        "signed_sanction_letter_and_KFS", "pdf", MimeType.PDF)
    ADDENDUM = ApolloDocument(
        "addendum", "pdf", MimeType.PDF)
