import bson
from admin.services.commercial_loan_details.commercial_loan_details_builder import CommercialLoanDetailsBuilder
from admin.services.commercial_loan_details.commercial_loan_details_fetch import CommercialLoanDetailsModel
from admin.services.commercial_loan_details.commercial_loans_kyc_service import CommercialLoansKycService
from admin.views.admin_view import AdminView
from dal.models.employees import Employee
from dal.models.employer import Employer
from dal.models.employments import Employments
from dal.models.sales_users import SalesUser
from starlette_admin import CollectionField, EnumField, HasMany, HasOne, StringField, FileField, IntegerField, ListField, BooleanField, action, row_action
from typing import Any, Dict, List, Optional, Union
from starlette.requests import Request
from admin.utils import DictToObj
from starlette_admin.exceptions import FormValidationError, ActionFailed
from starlette.requests import Request
from typing import Any

from services.storage.uploads.s3_upload_service import S3UploadService


def get_sales_user_data(request: Request):
    if request.state.user is not None:
        return [request.state.user["roles"], request.state.user["sales_id"]]
    raise ActionFailed("User Not Present in the Database")


class CommercialLoansView(AdminView):
    identity = "commercial_loans"
    name = "Commercial Loan"
    label = "Apollo Loans"
    icon = "fa fa-coins"
    model = Employer
    search_builder = False
    pk_attr = "_id"
    fields = [
        StringField("_id", label="Employer ID"),
        HasOne(
            "employerId",
            identity="employer",
            label="Select Employer ID",
            exclude_from_detail=True,
            exclude_from_edit=True,
            exclude_from_list=True,
            required=True
        ),
        StringField("companyName", label="Company Name",
                    read_only=True, exclude_from_create=True),
        CollectionField("commercial_loan_details", fields=[
            IntegerField("annual_turn_over", required=True),
            StringField("business_category", required=True),
            StringField("industry_type", required=True),
            EnumField("constitution", required=True, choices=[
                      ("Proprietorship", "Proprietorship"), ("Private Limited", "Private Limited"), ("Proprietor", "Proprietor"), ("private limited", "private limited")]),
        ]),
        CollectionField("employer_address", fields=[
            StringField("address", required=True),
            StringField("city", required=True),
            StringField("state", required=True),
            StringField("pin", required=True),
        ]),
        CollectionField("disbursement_bank_account", fields=[
            StringField("account_number", required=True),
            StringField("ifsc", required=True),
        ]),
        CollectionField("employer_ids", fields=[
            StringField("pan_number", required=True),
            StringField("gst_number", required=True, label="GST Number"),
            StringField(
                "registration_number",
                placeholder="NA",
                label="Company Registration Number"
            ),
            StringField(
                "udyam_number",
                placeholder="NA"
            ),
            StringField(
                "duns_number",
                placeholder="999999999"
            ),
        ]),
        ListField(
            CollectionField("promoters", fields=[
                HasOne("employee", identity="employees", required=True),
                StringField("aadhaar", required=True),
                StringField("pan", required=True),
                StringField("currentAddress", required=True,
                            label="Current Address"),
                BooleanField("key_promoter", required=True,
                             label="Is Key Promoter ?")
            ], required=True),
            required=True),
        CollectionField("document_uploads", fields=[
            FileField(
                "gst_certificate",
                required=True,
                display_template="fields/file.html",
                exclude_from_list=True),
            FileField(
                "bank_statement",
                required=True,
                display_template="fields/file.html",
                exclude_from_list=True),
            FileField(
                "bureau",
                required=True,
                display_template="fields/file.html",
                exclude_from_list=True),
            FileField(
                "incorporation_certificate",
                required=True,
                display_template="fields/file.html",
                exclude_from_list=True)
        ], required=True),
    ]

    exclude_fields_from_list = ["promoters"]

    def is_accessible(self, request: Request) -> bool:
        return "commercial_loans" in request.state.user["roles"]

    def can_create(self, request: Request) -> bool:
        return "commercial_loans_create" in request.state.user["roles"]

    def can_edit(self, request: Request, obj: Any = None) -> bool:
        return False

    def can_delete(self, request: Request, obj: Any = None) -> bool:
        return False

    async def is_row_action_allowed(self, request: Request, name: str) -> bool:
        roles = request.state.user["roles"]
        if name in ["delete", "edit"]:
            return "super-admin" in roles
        if name == "create":
            return "commercial_loans_create" in roles
        if name in ["view"]:
            return "commercial_loans" in roles
        if name in roles:
            return True
        return "super-admin" in roles

    async def find_by_pk(self, request: Request, pk):
        commercial_loan_details = CommercialLoanDetailsModel.find_one({
                                                                      "_id": pk})
        if commercial_loan_details is None:
            return None
        return DictToObj(commercial_loan_details)

    async def find_all(self, request: Request, skip: int = 0, limit: int = 100,
                       where: Union[Dict[str, Any], str, None] = None,
                       order_by: Optional[List[str]] = None) -> List[Any]:
        sort = self.create_sort_key(order_by)
        res = CommercialLoanDetailsModel.find({}, skip, limit, sort)
        find_all_res = []
        for employer in res:
            find_all_res.append(DictToObj(employer))

        return find_all_res

    async def count(self, request: Request, where: Union[Dict[str, Any], str, None] = None) -> int:
        return CommercialLoanDetailsModel.count({})

    async def create(self, request: Request, data: Dict):
        """Validate loan details are not already present"""
        existing_loan_details = self.model.find_one({
            "_id": data["employerId"],
            "commercialLoanDetails": {"$exists": 1}
        })
        errors = {}
        if existing_loan_details is not None:
            errors["employerId"] = "loan details already exist for provided employer id"

        if len(errors):
            raise FormValidationError(errors)
        loan_details_service = CommercialLoanDetailsBuilder(data["employerId"])
        loan_details_service.add_loan_details(
            **data["commercial_loan_details"])
        loan_details_service.add_address(**data["employer_address"])
        loan_details_service.add_promoters(
            promoters=data["promoters"])

        loan_details_service.add_employer_government_ids(
            **data["employer_ids"]
        )
        loan_details_service.add_employer_bank_account(
            **data["disbursement_bank_account"]
        )
        loan_details_service.upload_documents(data["document_uploads"])
        loan_details_service.write_to_db()
        return DictToObj(data)

    async def edit(self, request: Request, pk, data: Dict):
        raise Exception("Not Supported")

    @row_action(
        name="commercial_loan_kyc",
        text="Loan KYC",
        icon_class="fas fa-id-card",
        confirmation="Are you sure you want to perform KYC for the selected loan?",
        submit_btn_text="Yes, proceed",
        submit_btn_class="btn-success",
        action_btn_class="btn-primary",
        exclude_from_list=True,
    )
    async def commercial_loan_kyc_action(self, request: Request, pk: str) -> str:
        roles = request.state.user["roles"]
        if "admin" not in roles and "super-admin" not in roles:
            raise ActionFailed("Insufficient User Permissions")
        kyc_service = CommercialLoansKycService(employer_id=pk)
        kyc_service.perform_kyc()
        return "KYC Completed for this loan"

    @row_action(
        name="commercial_loan_loc",
        text="Create Apollo LOC",
        icon_class="fas fa-file-alt",
        confirmation="Are you sure you want to create apollo loc for the selected loan?",
        submit_btn_text="Yes, proceed",
        submit_btn_class="btn-warning",
        action_btn_class="btn-danger",
        exclude_from_list=True,
        form=open("admin/templates/commercial_loans/create_loc_form.html").read()
    )
    async def commercial_loan_loc_action(self, request: Request, pk: str) -> str:
        roles = request.state.user["roles"]
        data = await request.form()
        offer_id = bson.ObjectId(data["loan_offer_id"])
        if "admin" not in roles and "super-admin" not in roles:
            raise ActionFailed("Insufficient User Permissions")
        kyc_service = CommercialLoansKycService(employer_id=pk)
        kyc_service.trigger_loc_creation(offer_id)
        return "LOC Creation Triggered for Employer"
