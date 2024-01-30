from datetime import datetime
import enum
from typing import Any, Dict, List, Optional, Union
import bson
from starlette.requests import Request
from admin.services.offers.offer_creation import create_offer
from admin.utils import DictToObj
from admin.views.admin_view import AdminView
from admin.models.offers import Offer
from dal.models.offer import Offers
from starlette_admin import BooleanField, DateField, HasOne, StringField, DateTimeField, EnumField, DecimalField, IntegerField
from starlette_admin.exceptions import ActionFailed


class LoanType(enum.Enum):
    COMMERCIAL = "COMMERCIAL"
    PERSONAL = "PERSONAL"


class LoanProvider(enum.Enum):
    apollo = "apollo"
    liquiloans = "liquiloans"


class OffersView(AdminView):
    document = Offer
    identity = "offer"
    name = "Offer"
    label = "Offers"
    icon = "fa fa-money-check"
    model = Offers
    pk_attr = "_id"
    fields = [
        StringField("_id", label="Offer Id"),
        StringField("employerId", label="employerId"),
        StringField("unipeEmployeeId", label="unipeEmployeeId"),
        # HasOne("employerId", identity="employer", required=True),
        # HasOne("unipeEmployeeId", identity="employees", required=True),
        EnumField("provider", enum=LoanProvider, required=True),
        EnumField("loanType", enum=LoanType, required=True),
        StringField("year", exclude_from_create=True),
        StringField("month", exclude_from_create=True),
        IntegerField("loanAmount", exclude_from_create=True),
        IntegerField("limitAmount", required=True),
        IntegerField("eligibleAmount", required=True),
        DateField("dueDate", required=True),
        BooleanField("live", exclude_from_create=True),
        BooleanField("availed", exclude_from_create=True),
        DateTimeField("availedAt", exclude_from_create=True),
        BooleanField("disbursed", exclude_from_create=True),
        StringField("employmentId", exclude_from_create=True),
        DecimalField("fees", required=True),
        BooleanField("paid", exclude_from_create=True),
        StringField("stage", exclude_from_create=True),
        DateTimeField("updatedAt", exclude_from_create=True),
        DateTimeField("disbursedAt", exclude_from_create=True),
        StringField("disbursementId", exclude_from_create=True),
        StringField("repaymentId", exclude_from_create=True),
        StringField("paidAmount", exclude_from_create=True)
    ]

    def can_create(self, request: Request) -> bool:
        roles = request.state.user["roles"]
        return "super_admin" in roles or "admin" in roles

    def can_edit(self, request: Request) -> bool:
        return False

    async def find_all(self, request: Request, skip: int = 0, limit: int = 100, where: Dict[str, Any] | str | None = None, order_by: List[str] | None = None) -> List[Any]:
        results = await super().find_all(request, skip, limit, where, order_by)
        # for result in results:
        #     result.convert_to_fk("unipeEmployeeId")
        #     result.convert_to_fk("employerId")
        return results

    async def create(self, request: Request, data: Dict[str, Any]) -> DictToObj:
        current_time = datetime.now()
        data["unipeEmployeeId"] = bson.ObjectId(data["unipeEmployeeId"])
        data["dueDate"] = datetime.fromisoformat(data["dueDate"].isoformat())
        data["fees"] = float(data["fees"])
        create_offer(
            unipe_employee_id=data["unipeEmployeeId"],
            employer_id=data["employerId"],
            due_date=data["dueDate"],
            limit_amount=data["limitAmount"],
            eligible_amount=data["eligibleAmount"],
            fees=data["fees"],
            loan_type=data["loanType"] or "PERSONAL",
            loan_provider=data["provider"] or "liquiloans",
            year=current_time.year,
            month=current_time.month
        )
        result = await super().create(request, data)
        result.convert_to_fk("unipeEmployeeId")
        result.convert_to_fk("employerId")
        return result
