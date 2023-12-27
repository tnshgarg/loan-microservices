import bson
from admin.views.admin_view import AdminView
from dal.models.employees import Employee
from dal.models.employer import Employer
from dal.models.sales_users import SalesUser
from starlette_admin import HasMany, HasOne, StringField
from typing import Any, Dict, List, Optional, Union
from starlette.requests import Request
from admin.utils import DictToObj
from starlette.requests import Request
from typing import Any

EMPLOYER_AGGREGATE_PIPELINE = [
    {'$match': {'commercialLoanDetails': {'$exists': 1}}},
    {'$unwind': {'path': '$commercialLoanDetails.promoters'}},
    {'$lookup': {'from': 'employees', 'localField': 'commercialLoanDetails.promoters',
                         'foreignField': '_id', 'as': 'employee'}}
]


class PromotersView(AdminView):
    identity = "promoters"
    name = "Promoters"
    label = "Promoters"
    icon = "fa fa-user-tie"
    model = Employee
    pk_attr = "_id"
    fields = [
        StringField("_id"),
        StringField("employeeName"),
        HasOne("loanDetails", identity="commercial_loans", label="Employer"),
        StringField("mobile"),

        StringField("companyName"),
        StringField("email"),
        StringField("gender"),
        StringField("nationality"),
        StringField("dob"),
        StringField("altMobile"),
        StringField("motherName"),
        StringField("qualification"),
        StringField("currentAddress"),

    ]

    async def is_accessible(self, request: Request) -> bool:
        roles = request.state.user["roles"]
        return "commercial_loans" in roles

    async def count(self, request, where):
        res = Employer.aggregate(
            pipeline=EMPLOYER_AGGREGATE_PIPELINE+[{"$unwind": {"path": "$employee"}}, {"$project": {"_id": 1}}])
        return len(list(res))

    async def find_all(self, request: Request, skip: int = 0, limit: int = 100,
                       where: Union[Dict[str, Any], str, None] = None,
                       order_by: Optional[List[str]] = None) -> List[Any]:

        # TODO: Check for Admin, RM and SM Conditions on what data to show

        res = Employer.aggregate(
            pipeline=EMPLOYER_AGGREGATE_PIPELINE + [{"$skip": skip}, {"$limit": limit}])
        find_all_res = []
        for employer_lead in res:
            promoter = employer_lead["employee"][0]
            promoter["loanDetails"] = DictToObj({"_id": employer_lead["_id"]})
            promoter["companyName"] = employer_lead.get("companyName")
            promoter["_id"] = str(promoter["_id"])
            find_all_res.append(DictToObj(promoter))

        return find_all_res

    async def find_by_pk(self, request: Request, pk):
        promoter = self.model.find_one({"_id": bson.ObjectId(pk)})

        if not promoter:
            return None

        related_employer = Employer.find_one(
            {"commercialLoanDetails.promoters": bson.ObjectId(pk)})
        if related_employer:
            promoter['related_employer'] = related_employer

        return DictToObj(promoter)
