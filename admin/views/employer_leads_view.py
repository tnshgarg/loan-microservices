from typing import Any, Dict, Iterable, List, Optional, Union

import bson
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette_admin import BaseModelView, StringField

from admin.services.bureau_fetch_service import BureauFetchService
from admin.utils import DictToObj
from dal.models.employer_leads import EmployerLeads


def trigger_bureau_fetch(inserted_employer_lead_object):
    name = inserted_employer_lead_object.name
    mobile = inserted_employer_lead_object.mobile
    pan = inserted_employer_lead_object.pan
    try:
        BureauFetchService().fetch_bureau_details(name, mobile, pan)
    except Exception as e:
        raise HTTPException(500, str(e))


class EmployerLeadsView(BaseModelView):
    identity = "employer_leads"
    name = "Employer Leads"
    label = "Employer Leads"
    icon = "fa fa-id-card"
    pk_attr = "_id"
    fields = [
        StringField("_id"),
        StringField("name"),
        StringField("mobile"),
        StringField("pan")
    ]

    class Meta:
        model = EmployerLeads

    async def count(self, request: Request, where: Union[Dict[str, Any], str, None] = None) -> int:
        filter_ = {}
        # if where is not None:
        #     filter_ = where
        employer_leads_res = self.Meta.model.find(filter_)
        return len(list(employer_leads_res))

    async def find_all(self, request: Request, skip: int = 0, limit: int = 100,
                       where: Union[Dict[str, Any], str, None] = None,
                       order_by: Optional[List[str]] = None) -> List[Any]:
        employer_leads_res = self.Meta.model.find({})
        employer_leads_res.skip(skip).limit(limit)
        order_by
        find_all_res = []
        for employer_lead in employer_leads_res:
            find_all_res.append(DictToObj(employer_lead))
        return find_all_res
        # values = list(db.values())
        # if order_by is not None:
        #     assert len(order_by) < 2, "Not supported"
        #     if len(order_by) == 1:
        #         key, dir = order_by[0].split(maxsplit=1)
        #         values.sort(key=lambda v: getattr(
        #             v, key), reverse=(dir == "desc"))

        # if where is not None and isinstance(where, (str, int)):
        #     values = filter_values(values, where)
        # if limit > 0:
        #     return values[skip: skip + limit]
        # return values[skip:]

    async def find_by_pk(self, request: Request, pk):
        employer_leads_res = EmployerLeads.find_one({"_id": bson.ObjectId(pk)})
        return DictToObj(employer_leads_res)

    async def create(self, request: Request, data: Dict):
        sales_id = request.state.user.get("sales_id")
        data["sales_id"] = bson.ObjectId(sales_id)

        employer_leads_insert_res = EmployerLeads.insert_one(data)
        inserted_id = employer_leads_insert_res.inserted_id
        data["_id"] = inserted_id
        inserted_employer_lead_object = DictToObj(data)

        await self.after_create(request, inserted_employer_lead_object)
        return inserted_employer_lead_object

    async def after_create(self, request: Request, obj: Any) -> None:
        trigger_bureau_fetch(obj)

    async def edit(self, request: Request, pk, data: Dict):
        employer_leads_update_res = EmployerLeads.update_one(
            filter_={"_id": bson.ObjectId(pk)},
            update={"$set": data}
        )
        data["_id"] = pk
        return DictToObj(data)

    async def delete(self, request: Request, pks: List[Any]) -> Optional[int]:
        object_ids_to_delete = [bson.ObjectId(pk) for pk in pks]
        employer_leads_delete_res = EmployerLeads.delete({
            "_id": {
                "$in": object_ids_to_delete
            }
        })
        deleted_document_count = employer_leads_delete_res.deleted_count
        return deleted_document_count
