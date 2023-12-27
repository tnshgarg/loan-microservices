

from admin.services.kyc.gridlines_kyc_service import GridlinesKYCService
from admin.services.kyc.karza_kyc_service import KarzaKycService
from dal.logger import get_app_logger
from dal.models.employees import Employee
from dal.models.employer import Employer
from dal.models.encrypted_bank_accounts import EncryptedBankAccounts
from dal.models.encrypted_government_ids import EncryptedGovernmentIds
from dal.models.offer import Offers
from kyc.config import Config
from services.ewa.apollo.loan_application_api import ApolloLoanApplicationHook
from starlette_admin.exceptions import ActionFailed


class CommercialLoansException(ActionFailed):
    pass


class CommercialLoansKycService:

    def __init__(self, employer_id) -> None:
        self.employer_id = employer_id
        self.employer_doc = Employer.find_one({"_id": employer_id})
        self.commercial_loan_details = self.employer_doc["commercialLoanDetails"]
        self.logger = get_app_logger("commercial-loans-kyc", Config.STAGE)
        self.karza_service = KarzaKycService(self.logger, Config.STAGE)
        self.gridlines_service = GridlinesKYCService(self.logger, Config.STAGE)

    def verify_pan(self, p_id, u_type="employee"):
        government_ids = EncryptedGovernmentIds.find({
            "pId": p_id,
            "provider": "karza",
            "type": "pan",
            "uType": u_type
        })
        kyc_pending = None
        for pan_details in government_ids:
            if pan_details.get("verifyStatus") not in ["INPROGRESS_CONFIRMATION", "SUCCESS"]:
                kyc_pending = pan_details
        if kyc_pending is not None:
            self.karza_service.pan_fetch_details(
                p_id=p_id,
                pan=kyc_pending["number"]
            )
            return "INPROGRESS_CONFIRMATION"
        else:
            raise Exception(
                f"No pan number found in db for {p_id}"
            )

    def verify_disbursement_bank_account(self):
        pending_bank_account = EncryptedBankAccounts.find_one({
            "pId": self.employer_id,
            "uType": "employerpass-disbursement",
            "verifyStatus": {"$nin": ["INPROGRESS_CONFIRMATION", "SUCCESS"]}
        })
        if pending_bank_account is not None:
            bank_account_data = pending_bank_account.get("data")
            self.gridlines_service.bank_verify_account(
                p_id=self.employer_id,
                u_type="employer-disbursement",
                account_number=bank_account_data["accountNumber"],
                ifsc=bank_account_data["ifsc"]
            )
            return "INPROGRESS_CONFIRMATION"
        return "SUCCESS"

    def perform_kyc(self):
        promoters = self.commercial_loan_details["promoters"]
        self.verify_pan(p_id=self.employer_id, u_type="employer")
        for promoter_id in promoters:
            self.verify_pan(p_id=promoter_id)
        self.verify_disbursement_bank_account()
        self.logger.info(
            "KYC verification completed for employer %s" % self.employer_id)
        return True

    def trigger_loc_creation(self, offer_id):
        key_promoter = self.commercial_loan_details["keyPromoter"]
        apollo_loan_application_hook = ApolloLoanApplicationHook(
            unipe_employee_id=key_promoter,
            offer_id=offer_id
        )
        offer_doc = Offers.find_one({"_id": offer_id})
        if offer_doc is None:
            raise CommercialLoansException(
                "Provided `offer_id` not found in db")
        if offer_doc["unipeEmployeeId"] != key_promoter or offer_doc["employerId"] != self.employer_id:
            raise CommercialLoansException(
                "please check employee id and employer id for this offer")
        if offer_doc["provider"] != "apollo" or offer_doc["loanType"] != "COMMERCIAL":
            raise CommercialLoansException(
                "Please check if offer is for `APOLLO` and loanType is `COMMERCIAL`"
            )
        apollo_loan_application_hook.post_event(
            action=ApolloLoanApplicationHook.Action.LOC,
            status=ApolloLoanApplicationHook.Status.CREATE
        )
        return True
