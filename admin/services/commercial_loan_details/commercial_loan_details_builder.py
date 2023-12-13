

import bson
from admin.services.commercial_loan_details.employer_loan_uploads_service import EmployerLoanDocumentsUploadService
from dal.models.employees import Employee
from dal.models.employer import Employer
from dal.models.employments import Employments
from dal.models.encrypted_bank_accounts import EncryptedBankAccounts
from dal.models.encrypted_government_ids import EncryptedGovernmentIds


class CommercialLoanDetailsBuilder:

    def __init__(self, employer_id) -> None:
        self.employer_id = employer_id
        self.s3_upload_service = EmployerLoanDocumentsUploadService(
            employer_id)
        self.details = {}
        self.errors = {}

    def add_loan_details(self,
                         annual_turn_over,
                         business_category,
                         constitution,
                         industry_type):
        self.details["annual_turn_over"] = annual_turn_over
        self.details["business_category"] = business_category
        self.details["constitution"] = constitution
        self.details["industry_type"] = industry_type

    def add_address(self, address, city, state, pin):
        self.details["address"] = address
        self.details["city"] = city
        self.details["state"] = state
        self.details["pin"] = pin

    def add_promoters(self, promoters, key_promoter):
        if key_promoter not in promoters:
            self.errors["keyPromoter"] = "keyPromoter should be included in promoters"

        self.details["keyPromoter"] = bson.ObjectId(key_promoter)
        self.details["promoters"] = []
        for promoter in promoters:
            promoter_id = bson.ObjectId(promoter)
            active_employment = Employments.find_one({
                "pId": promoter_id,
                "employerId": self.employer_id,
                "active": True
            })
            self.details["promoters"].append(promoter_id)
            if active_employment is None:
                self.errors["promoters"] = f"{promoter_id} is not employed for the provided employer"

    def upsert_government_id(self, number, type):
        government_id = {
            "pId": self.details["keyPromoter"],
            "uType": "employee",
            "type": type
        }
        existing_id = EncryptedGovernmentIds.find_one(government_id)
        if existing_id is None or existing_id["verifyStatus"] != "SUCCESS":
            EncryptedGovernmentIds.update_one(government_id, {"$set": {
                "verifyStatus": "PENDING",
                "provider": "karza",
                "number": number
            }})
        else:
            EncryptedGovernmentIds.insert_one({
                **government_id,
                "verifyStatus": "PENDING",
                "provider": "karza",
                "number": number
            })

    def add_promoter_details(self, pan_number, aadhaar_number, address):
        """Verify Possible Ids and generate tempate objects for key promoter"""
        self.upsert_government_id(pan_number, "pan")
        self.upsert_government_id(aadhaar_number, "aadhaar")
        Employee.update_one({
            "_id": self.details["keyPromoter"],
            "currentAddress": {"$exists": 0}
        }, {
            "$set": {
                "currentAddress": address,
                "profileComplete": True
            }
        }, upsert=False)

    def add_employer_government_ids(self, pan_number, gst_number, registration_number="NA", udyam_number="NA", duns_number="999999999"):
        """update these details in loan details"""
        self.details["gstNumber"] = gst_number
        self.details["companyRegistrationNumber"] = registration_number
        self.details["udyam_registration_number"] = udyam_number
        self.details["duns_number"] = duns_number
        EncryptedGovernmentIds.update_one({
            "pId": self.employer_id,
            "type": "pan",
            "uType": "employer"
        }, {
            "$set": {
                "number": pan_number
            }
        }, upsert=True)

    def add_employer_bank_account(self, account_number, ifsc):
        EncryptedBankAccounts.update_one({
            "pId": self.employer_id,
            "uType": "employer-disbursement"
        }, {
            "$set": {
                "data.accountNumber": account_number,
                "data.ifsc": ifsc,
                "verifyStatus": "pending"
            }
        })

    def upload_documents(self, uploaded_documents):
        for document_key in ["gst_certificate", "bank_statement", "bureau", "incorporation_certificate"]:
            upload, status = uploaded_documents[document_key]
            self.s3_upload_service.upload_document(
                document_type=document_key,
                form_file=upload.file,
                content_type=upload.content_type
            )

    def write_to_db(self):
        Employer.update_one({"_id": self.employer_id}, {
            "$set": {
                "commercialLoanDetails": self.details
            }
        })
