import bson
from admin.views.admin_view import AdminView
from dal.models.sales_users import SalesUser
from starlette_admin import CollectionField,  StringField
from typing import Any, Dict, List, Optional, Union
from starlette.requests import Request
from admin.utils import DictToObj
from starlette.requests import Request
from typing import Any
from bson import ObjectId
from dal.models.scheduled_jobs import ScheduledJob

REPAYMENT_RECONCILATION_PROJECTION = {
    "provider": "Razorpay",
    "payment_id": "$body.payload.payment.entity.id",
    "status": 1,
    "amount": "$body.payload.payment.entity.amount",
    "description": "$body.payload.payment.entity.description",
    "email": "$body.payload.payment.entity.email",
    "contact": "$body.payload.payment.entity.contact",
    "notes": "$body.payload.payment.entity.notes",
}


class RepaymentReconcilation(AdminView):

    identity = "repayment_reconcilation"
    name = "Repayment Reconcilation"
    label = "Repayment Reconcilation"
    icon = "fa fa-inr"
    model = ScheduledJob
    pk_attr = "_id"
    fields = [
        StringField("_id", read_only=True),
        StringField("provider", read_only=True),
        StringField("payment_id", read_only=True),
        StringField("status", read_only=True),
        StringField("amount", read_only=True),
        StringField("description", read_only=True),
        StringField("email", read_only=True),
        StringField("contact", read_only=True),
        CollectionField("notes", fields=[
            StringField("repaymentId"),
            StringField("employerId")
        ]),
    ]
    custom_filter = {
        "body.payload.payment.entity.amount": {"$gt": 0},
        "body.event": "payment.captured",
        "status": {"$in": ["ERROR", "OPS_ISSUE", "IN_QUEUE"]},
        "eventType": "WEBHOOK_PAYMENT_UPDATE:RAZORPAY"
    }

    async def find_all(self, request: Request, skip: int = 0, limit: int = 100,
                       where: Union[Dict[str, Any], str, None] = None,
                       order_by: Optional[List[str]] = None) -> List[Any]:

        username = request.session.get("username", None)
        if username:
            user_data = SalesUser.find_one({"email": username})
            if user_data:
                user_type = user_data.get("type")
                sales_user_id = user_data.get("_id")
                print("User Type:", user_type)

        res = self.model.aggregate(pipeline=[
            {'$match': self.custom_filter},
            {'$project': REPAYMENT_RECONCILATION_PROJECTION}
        ])

        # order_by
        find_all_res = []
        for employer_lead in res:
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

        customFilter = {**self.custom_filter, **{"_id": pk}}
        document = self.model.find_one(
            customFilter, projection=REPAYMENT_RECONCILATION_PROJECTION)

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

        if len(repayment_id) > 0:
            update_res = self.model.update_one(
                filter_={"_id": bson.ObjectId(pk)},
                update={"$set": {"body.payload.payment.entity.notes": {
                    "repaymentId": repayment_id}}}
            )
        elif len(employer_id) > 0:
            update_res = self.model.update_one(
                filter_={"_id": bson.ObjectId(pk)},
                update={"$set": {"body.payload.payment.entity.notes": {
                    "employerId": employer_id}}}
            )

        else:
            # TODO: Either Repayment Id or Employer Id must be there
            raise Exception("Invalid Update")

        data["_id"] = pk
        return DictToObj(data)