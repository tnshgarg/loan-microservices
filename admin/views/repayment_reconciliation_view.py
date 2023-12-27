from datetime import datetime
from random import randint
import bson
import pytz
from admin.constants import BusinessType
from admin.views.admin_view import AdminView
from dal.models.sales_users import SalesUser
from starlette_admin import CollectionField, EnumField,  StringField, TextAreaField, TinyMCEEditorField
from typing import Any, Coroutine, Dict, List, Optional, Union
import os
from starlette.requests import Request
from admin.utils import DictToObj
from starlette.requests import Request
from typing import Any
from bson import ObjectId
from dal.models.scheduled_jobs import ScheduledJob

REPAYMENT_RECONCILIATION_FILTER = {
    "body.payload.payment.entity.amount": {"$gt": 0},
    "body.event": "payment.captured",
    "status": {"$in": ["ERROR", "OPS_ISSUE", "IN_QUEUE"]},
    "eventType": "WEBHOOK_PAYMENT_UPDATE:RAZORPAY"
}
REPAYMENT_RECONCILIATION_PROJECTION = {
    "provider": "Razorpay",
    "payment_id": "$body.payload.payment.entity.id",
    "status": 1,
    "amount": "$body.payload.payment.entity.amount",
    "description": "$body.payload.payment.entity.description",
    "email": "$body.payload.payment.stringentity.email",
    "contact": "$body.payload.payment.entity.contact",
    "notes": "$body.payload.payment.entity.notes",
    "account_id": "$body.account_id",
    "message": "$context.exception.message",
    "error": {"$concat": ["<details><summary>", "$context.exception.message", "</summary><pre><code>", "$context.exception.stacktrace", "</code></pre></details>"]}
}

APOLLO_ACCOUNT_ID = os.getenv("APOLLO_ACCOUNT_ID")
LIQUILOANS_ACCOUNT_ID = os.getenv("LIQUILOANS_ACCOUNT_ID")


class RepaymentReconciliationView(AdminView):
    identity = "repayment_reconciliation"
    name = "Repayment Reconciliation"
    label = "Repayment Reconciliation"
    icon = "fa fa-inr"
    model = ScheduledJob
    pk_attr = "_id"
    fields = [
        StringField("_id", read_only=True, disabled=True),
        StringField("created_at", read_only=True, disabled=True),
        StringField("provider", read_only=True, disabled=True),
        StringField("account_id", read_only=True),
        StringField("account_name", read_only=True),
        StringField("payment_id", read_only=True, disabled=True),
        StringField("status", read_only=True, disabled=True),
        StringField("amount", read_only=True, disabled=True),
        StringField("description", read_only=True, disabled=True),
        StringField("email", read_only=True, disabled=True),
        StringField("contact", read_only=True, disabled=True),

        CollectionField("notes", fields=[
            StringField("repaymentId"),
            StringField("employerId")
        ]),
        EnumField("businessType", enum=BusinessType),
        StringField("message", exclude_from_detail=True,
                    read_only=True, disabled=True),
        TinyMCEEditorField("error", exclude_from_list=True,
                           read_only=True, disabled=True, exclude_from_edit=True)
    ]
    custom_filter = {}

    def is_accessible(self, request: Request) -> bool:
        roles = request.state.user["roles"]
        return "admin" in roles or "super-admin" in roles

    def can_edit(self, request: Request) -> bool:
        return self.is_accessible(request)

    async def count(self, request: Request, where: Dict[str, Any] | str | None = None) -> Coroutine[Any, Any, int]:
        res = self.model.aggregate(pipeline=[
            {'$match': REPAYMENT_RECONCILIATION_FILTER},
            {'$count': "ct"}
        ])
        res = res.try_next()
        if res is None:
            return 0
        return res.get("ct", 0)

    async def find_all(self, request: Request, skip: int = 0, limit: int = 100,
                       where: Union[Dict[str, Any], str, None] = None,
                       order_by: Optional[List[str]] = None) -> List[Any]:

        # TODO: Check for Admin, RM and SM Conditions on what data to show
        sort_key = self.create_sort_key(order_by)
        res = self.model.aggregate(pipeline=[
            {'$match': REPAYMENT_RECONCILIATION_FILTER},
            {"$sort": {k: v for k, v in sort_key}},
            {"$skip": skip},
            {"$limit": limit},
            {'$project': REPAYMENT_RECONCILIATION_PROJECTION}
        ])
        find_all_res = []
        for employer_lead in res:
            employer_lead["created_at"] = employer_lead["_id"].generation_time
            employer_lead["created_at"] = employer_lead["created_at"].astimezone(
                pytz.timezone("Asia/Kolkata"))
            employer_lead["amount"] /= 100
            if employer_lead["account_id"] == APOLLO_ACCOUNT_ID:
                employer_lead["account_name"] = "apollo"
            else:
                employer_lead["account_name"] = "liquiloans"
            find_all_res.append(DictToObj(employer_lead))
        return find_all_res

    async def find_by_pk(self, request: Request, pk: str) -> Any:
        if not pk:
            raise ValueError("Primary key (pk) must be provided")

        if not isinstance(pk, ObjectId):
            try:
                pk = ObjectId(pk)
            except Exception as e:
                raise ValueError("Invalid primary key format") from e
        document = self.model.find_one({
            "_id": pk
        }, projection=REPAYMENT_RECONCILIATION_PROJECTION)

        if document:
            return DictToObj(document)
        else:
            return None

    async def edit(self, request: Request, pk: str, data: Dict) -> Any:
        if not pk:
            raise ValueError("Primary key (pk) must be provided")

        if not isinstance(pk, ObjectId):
            try:
                pk = ObjectId(pk)
            except Exception as e:
                raise ValueError("Invalid primary key format") from e

        repayment_id = data["notes"]["repaymentId"]
        employer_id = data["notes"]["employerId"]

        update = {
            "contentHash": f"ops-portal-reconciliation-view-{datetime.now().timestamp()}",
            "status": "RETRY",
        }
        if len(repayment_id) > 0:
            update["body.payload.payment.entity.notes"] = {
                "repaymentId": repayment_id}
            self.model.update_one(
                filter_={"_id": bson.ObjectId(pk)},
                update={"$set": update})
        elif len(employer_id) > 0:
            update["body.payload.payment.entity.notes"] = {
                "employerId": employer_id}
            self.model.update_one(
                filter_={"_id": bson.ObjectId(pk)},
                update={"$set": update})
        else:
            # TODO: Either Repayment Id or Employer Id must be there
            raise Exception("Invalid Update")

        data["_id"] = pk
        return DictToObj(data)
