import bson
from admin.views.admin_view import AdminView
from dal.models.employees import Employee
from dal.models.employer import Employer
from dal.models.sales_users import SalesUser
from starlette_admin import CollectionField, HasMany, HasOne, StringField
from typing import Any, Dict, List, Optional, Union
from starlette.requests import Request
from admin.utils import DictToObj
from starlette.requests import Request
from typing import Any


class CommercialLoansView(AdminView):

    identity = "commercial_loans"
    name = "Commercial Loans"
    label = "Commercial Loans"
    icon = "fa fa-university"
    model = Employer
    pk_attr = "_id"
    # exclude_fields_from_edit=["commercialLoanDetails.duns_number"]
    fields = [
        StringField("_id"),
        HasMany("promoters", identity="promoters"),
        HasMany("keyPromoter", identity="promoters"),
        CollectionField("commercialLoanDetails", fields=[
            StringField("annual_turn_over"),
            StringField("address"),
            StringField("business_category"),
            StringField("city"),
            StringField("companyRegistrationNumber"),
            StringField("constitution"),
            StringField("duns_number"),
            StringField("industry_type"),
            StringField("pin"),
            StringField("state"),
            StringField("udyam_registration_number"),
        ]),
    ]

    async def find_all(self, request: Request, skip: int = 0, limit: int = 100,
                       where: Union[Dict[str, Any], str, None] = None,
                       order_by: Optional[List[str]] = None) -> List[Any]:
        if where is None:
            where = {"commercialLoanDetails": {"$exists": 1}}

        username = request.session.get("username", None)

        if username:
            user_data = SalesUser.find_one({"email": username})
            if user_data:
                userType = user_data.get("type")
                userSalesId = user_data.get("_id")
                print("User Type:", userType)

        if userSalesId and (userType == "sm" or userType == "rm"):
            where.update({
                "salesUsers": {
                    "$elemMatch": {"salesId": userSalesId}
                }
            })

        res = Employer.find(where).skip(skip).limit(limit)
        find_all_res = []
        for employer in res:
            employer_dict = DictToObj(employer)
            promoters = employer.get(
                'commercialLoanDetails', {}).get('promoters', [])
            key_promoter_id = employer.get(
                'commercialLoanDetails', {}).get('keyPromoter')

            if promoters:
                promoter_docs = Employee.find({"_id": {"$in": promoters}})
                employer_dict.promoters = [
                    DictToObj(promoter) for promoter in promoter_docs]

            if key_promoter_id:
                key_promoter_doc = Employee.find(
                    {"_id": bson.ObjectId(key_promoter_id)})
                employer_dict.keyPromoter = [
                    DictToObj(key_promoter) for key_promoter in key_promoter_doc]

            employer_dict.commercialLoanDetails["duns_number"] = "9999999999"
            find_all_res.append(employer_dict)

        return find_all_res
