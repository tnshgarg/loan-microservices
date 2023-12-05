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
    name = "Commercial Loans"
    label = "Commercial Loans"
    icon = "fa fa-coins"
    model = Employer
    pk_attr = "_id"
    fields = [
        StringField("_id"),
        HasOne("keyPromoter", identity="promoters"),
        CollectionField("commercialLoanDetails", fields=[
            # HasMany("promoters", identity="promoters"),
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

    async def find_by_pk(self, request: Request, pk):
        employer = await super().find_by_pk(request, pk)
        employer.commercialLoanDetails["keyPromoter"] = DictToObj({
            "_id": employer.commercialLoanDetails["keyPromoter"]})
        # employer.commercialLoanDetails["promoters"] = [{"_id": promoter_id}
        #                                                for promoter_id in employer.commercialLoanDetails["promoters"]]
        return employer

    async def find_all(self, request: Request, skip: int = 0, limit: int = 100,
                       where: Union[Dict[str, Any], str, None] = None,
                       order_by: Optional[List[str]] = None) -> List[Any]:

        [user_type, sales_user_id] = get_sales_user_data(request)

        where = create_where_filter(user_type, sales_user_id)

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

    async def count(self, request: Request, where: Union[Dict[str, Any], str, None] = None) -> int:
        [userType, userSalesId] = get_sales_user_data(request)

        filter_ = create_where_filter(userType, userSalesId)
        res = self.model.find(filter_)
        return len(list(res))
