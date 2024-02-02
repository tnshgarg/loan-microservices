import os
from typing import Any, Dict, Iterable, List, Optional, Union

import bson
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette_admin import BaseModelView, HasOne, StringField, URLField

from admin.services.bureau.bureau_fetch_service import BureauFetchService
from admin.services.bureau.s3_report_service import S3ReportService
from admin.utils import DictToObj
from dal.logger import get_app_logger
from dal.models.employer_leads import EmployerLeads
from dal.models.risk_profile import RiskProfile
from dal.models.sales_users import SalesUser
from kyc.config import Config


def trigger_bureau_fetch(inserted_object):
    name = inserted_object.name
    mobile = inserted_object.mobile
    pan = inserted_object.pan
    employer_id = inserted_object.employer_id
    try:
        BureauFetchService().fetch_bureau_details(name, mobile, pan, employer_id)
    except Exception as e:
        raise HTTPException(500, str(e))


def get_presigned_url(pan):
    risk_profile_find_res = RiskProfile.find_one({"pan": pan})
    s3_key = risk_profile_find_res.get("s3Key")
    if not s3_key:
        return None

    stage = Config.STAGE
    logger = get_app_logger("ops-microservice", stage)
    presigned_url = S3ReportService(stage, logger).create_presigned_url(s3_key)
    return presigned_url


def create_search_filter(sales_user, term):
    filter_ = {}
    if sales_user["roles"] in [SalesUser.Type.RM, SalesUser.Type.SM]:
        filter_["sales_id"] = bson.ObjectId(sales_user["sales_id"])

    if term is None or not isinstance(term, (str, int)):
        return filter_

    expressions = []
    for field in EmployerLeadsView.fields:
        if not field.exclude_from_list:
            expressions.append(
                {
                    field.name: {
                        "$regex": str(term),
                        "$options": "i"
                    }
                }
            )
    filter_["$or"] = expressions
    return filter_


def create_sorter(order_by):
    sorter = []
    if len(order_by):
        for field_info in order_by:
            field, order = field_info.split(maxsplit=1)
            direction = 1 if order == "asc" else -1
            sorter.append((field, direction))
    else:
        sorter.append(("$natural", -1))

    return sorter

# TODO: [TECHDEBT] This is not useing the appropriate base class


class EmployerLeadsView(BaseModelView):
    identity = "employer_leads"
    name = "Employer Leads"
    label = "Employer Leads"
    icon = "fa fa-file-invoice"
    pk_attr = "_id"
    fields = [
        StringField("_id"),
        StringField("name"),
        StringField("mobile"),
        StringField("pan"),
        StringField("bureauScore", label="Bureau Score"),
        StringField("dpd6Months", label="DPD 6 Months (30+)"),
        StringField("dpd2Years", label="DPD 2 Years (90+)"),
        StringField("writeoff"),
        StringField("settlement"),
        StringField("remarks"),
        StringField("employerLevel", label="Employer Score"),
        HasOne("employerId",
               identity="employer",
               label="Employer ID"),
        # add status field, try badge with tooltip
        StringField("status"),
        URLField("url", label="Download JSON")
    ]
    exclude_fields_from_list = ["_id"]
    exclude_fields_from_create = ["bureauScore", "dpd6Months", "dpd2Years",
                                  "writeoff", "settlement", "remarks", "employerLevel",
                                  "status", "url"]
    exclude_fields_from_edit = exclude_fields_from_create

    class Meta:
        model = EmployerLeads

    def can_edit(self, request: Request) -> bool:
        return "super-admin" in request.state.user["roles"]

    def can_delete(self, request: Request) -> bool:
        return "super-admin" in request.state.user["roles"]

    async def count(self, request: Request, where: Union[Dict[str, Any], str, None] = None) -> int:
        filter_ = create_search_filter(request.state.user, where)
        find_res = self.Meta.model.find(filter_)
        return len(list(find_res))

    async def find_all(self, request: Request, skip: int = 0, limit: int = 100,
                       where: Union[Dict[str, Any], str, None] = None,
                       order_by: Optional[List[str]] = None) -> List[Any]:
        filter_ = create_search_filter(request.state.user, where)
        sorter = create_sorter(order_by)
        find_res = self.Meta.model.find(filter_).sort(
            sorter).skip(skip).limit(limit)
        find_res_objects = []
        for doc in find_res:
            pan = doc["pan"]
            # ifadmin
            doc["url"] = get_presigned_url(pan)
            if "employerId" not in doc:
                doc["employerId"] = None
            else:
                doc["employerId"] = DictToObj({"_id": doc["employerId"]})
            find_res_objects.append(DictToObj(doc))
        return find_res_objects

    async def find_by_pk(self, request: Request, pk):
        find_one_res = self.Meta.model.find_one(
            {"_id": bson.ObjectId(pk)})
        pan = find_one_res["pan"]
        find_one_res["url"] = get_presigned_url(pan)
        if "employerId" not in find_one_res:
            find_one_res["employerId"] = None
        else:
            find_one_res["employerId"] = DictToObj(
                {"_id": find_one_res["employerId"]})
        return DictToObj(find_one_res)

    async def create(self, request: Request, data: Dict):
        sales_id = request.state.user.get("sales_id")
        data["sales_id"] = bson.ObjectId(sales_id)
        data["status"] = self.Meta.model.Status.PENDING
        data["employer_id"] = data.get("employer_id", None)
        insert_res = self.Meta.model.insert_one(data)
        inserted_id = insert_res.inserted_id
        data["_id"] = inserted_id
        inserted_object = DictToObj(data)

        await self.after_create(request, inserted_object)
        return inserted_object

    async def after_create(self, request: Request, obj: Any) -> None:
        trigger_bureau_fetch(obj)

    async def edit(self, request: Request, pk, data: Dict):
        update_res = self.Meta.model.update_one(
            filter_={"_id": bson.ObjectId(pk)},
            update={"$set": data}
        )
        data["_id"] = pk
        return DictToObj(data)

    async def delete(self, request: Request, pks: List[Any]) -> Optional[int]:
        object_ids_to_delete = [bson.ObjectId(pk) for pk in pks]
        delete_res = self.Meta.model.delete({
            "_id": {
                "$in": object_ids_to_delete
            }
        })
        deleted_document_count = delete_res.deleted_count
        return deleted_document_count
