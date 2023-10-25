
from dataclasses import dataclass


class MimeType:
    PDF = "application/pdf"
    ZIP = "application/zip"
    JPEG = "image/jpeg"
    JSON = "application/json"


@dataclass
class ApolloDocument:
    name: str
    extension: str
    mime_type: str
    internal: str = False

    @property
    def upload_key(self):
        return f"{self.name}.{self.extension}"


class ApolloPartnerTag:
    LOC = "UEC"
    DISBURSEMENT = "UED"


ApolloDocumentLevel = ApolloPartnerTag


class ApolloDocumentList:
    PAN = ApolloDocument("pan_uidai_xml", "json", MimeType.JSON)
    AADHAAR = ApolloDocument("aadhar_uidai_xml", "zip", MimeType.ZIP)
    SELFIE = ApolloDocument("selfie", "jpeg", MimeType.JPEG)
    LIVENESS_CHECK = ApolloDocument(
        "liveliness_output", "json", MimeType.JSON)
    SALARY_SLIP = ApolloDocument("salary_slip", "pdf", MimeType.PDF)

    SIGNED_LOAN_AGREEMENT = ApolloDocument(
        "loan_agreement", "pdf", MimeType.PDF, internal=True)
    SIGNED_SL_KFS = ApolloDocument(
        "signed_sanction_letter_and_KFS", "pdf", MimeType.PDF, internal=True)
    SIGNED_ADDENDUM = ApolloDocument(
        "addendum", "pdf", MimeType.PDF, internal=True)
    LOAN_AGREEMENT = ApolloDocument(
        "generated_loan_agreement", "pdf", MimeType.PDF, internal=True)
    SL_KFS = ApolloDocument("sanction_letter_and_KFS",
                            "pdf", MimeType.PDF, internal=True)
    ADDENDUM = ApolloDocument(
        "generated_addendum", "pdf", MimeType.PDF, internal=True)
    COMBINED_LA_ADDENDUM = ApolloDocument("la_and_addendum",
                                          "pdf", MimeType.PDF, internal=True)
