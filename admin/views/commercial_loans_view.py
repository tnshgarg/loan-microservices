import bson
from admin.services.commercial_loan_details.commercial_loan_details_builder import CommercialLoanDetailsBuilder
from admin.services.commercial_loan_details.commercial_loan_details_fetch import CommercialLoanDetailsModel
from admin.views.admin_view import AdminView
from dal.models.employees import Employee
from dal.models.employer import Employer
from dal.models.employments import Employments
from dal.models.sales_users import SalesUser
from starlette_admin import CollectionField, EnumField, HasMany, HasOne, StringField, FileField, IntegerField, ListField, BooleanField
from typing import Any, Dict, List, Optional, Union
from starlette.requests import Request
from admin.utils import DictToObj
from starlette_admin.exceptions import FormValidationError
from starlette.requests import Request
from typing import Any


def create_where_filter(userType: str, userSalesId: bson.ObjectId):
    where = {"commercialLoanDetails": {"$exists": 1}}
    if userSalesId and (userType == "sm" or userType == "rm"):
        where.update({
            "salesUsers": {
                "$elemMatch": {"salesId": userSalesId}
            }
        })
    return where


def get_sales_user_data(request: Request):
    if request.state.user is not None:
        return [request.state.user["roles"], request.state.user["sales_id"]]
    raise ActionFailed("User Not Present in the Database")


class CommercialLoansView(AdminView):
    identity = "commercial_loans"
    name = "Commercial Loan"
    label = "Commercial Loans"
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
                exclude_from_list=True),
            FileField(
                "bank_statement",
                required=True,
                exclude_from_list=True),
            FileField(
                "bureau",
                required=True,
                exclude_from_list=True),
            FileField(
                "incorporation_certificate",
                required=True,
                exclude_from_list=True)
        ], required=True),
    ]

    exclude_fields_from_list = ["promoters"]

    async def find_by_pk(self, request: Request, pk):
        commercial_loan_details = CommercialLoanDetailsModel.find_one({
                                                                      "_id": pk})
        if commercial_loan_details is None:
            return None
        return DictToObj(commercial_loan_details)

    async def find_all(self, request: Request, skip: int = 0, limit: int = 100,
                       where: Union[Dict[str, Any], str, None] = None,
                       order_by: Optional[List[str]] = None) -> List[Any]:

        [user_type, sales_user_id] = get_sales_user_data(request)

        where = create_where_filter(user_type, sales_user_id)
        sort = self.create_sort_key(order_by)
        res = CommercialLoanDetailsModel.find(where, skip, limit, sort)
        find_all_res = []
        for employer in res:
            # promoters = employer.get(
            #     'commercialLoanDetails', {}).get('promoters', [])
            # key_promoter_id = employer.get(
            #     'commercialLoanDetails', {}).get('keyPromoter')

            # if promoters:
            #     promoters = employer["commercialLoanDetails"]["promoters"]
            #     employer["promoters"] = [
            #         DictToObj({"_id": str(promoter)}) for promoter in promoters
            #     ]

            # if key_promoter_id:
            #     employer["keyPromoter"] = DictToObj({"_id": str(
            #         employer["commercialLoanDetails"]["keyPromoter"])})
            find_all_res.append(DictToObj(employer))

        return find_all_res

    async def count(self, request: Request, where: Union[Dict[str, Any], str, None] = None) -> int:
        [userType, userSalesId] = get_sales_user_data(request)

        filter_ = create_where_filter(userType, userSalesId)
        res = self.model.find(filter_)
        return len(list(res))

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
            promoters=data["promoter_details"]["promoters"], key_promoter=data["promoter_details"]["keyPromoter"])
        loan_details_service.add_promoter_details(
            pan_number=data["promoter_details"]["pan"],
            aadhaar_number=data["promoter_details"]["aadhaar"],
            address=data["promoter_details"]["currentAddress"],
        )

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
