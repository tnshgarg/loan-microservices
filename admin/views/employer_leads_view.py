from typing import Any, Dict, Iterable, List, Optional, Union

import bson
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette_admin import BaseModelView, StringField

from admin.services.bureau_fetch_service import BureauFetchService
from admin.utils import DictToObj
from dal.models.employer_leads import EmployerLeads
from dal.models.sales_users import SalesUser


def trigger_bureau_fetch(inserted_object):
    name = inserted_object.name
    mobile = inserted_object.mobile
    pan = inserted_object.pan
    try:
        BureauFetchService().fetch_bureau_details(name, mobile, pan)
    except Exception as e:
        raise HTTPException(500, str(e))


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
    if order_by is not None:
        for field_info in order_by:
            field, order = field_info.split(maxsplit=1)
            direction = 1 if order == "asc" else -1
            sorter.append((field, direction))
    return sorter


class EmployerLeadsView(BaseModelView):
    identity = "employer_leads"
    name = "Employer Leads"
    label = "Employer Leads"
    icon = "fa fa-id-card"
    pk_attr = "_id"
    fields = [
        StringField("_id", exclude_from_list=True),
        StringField("name"),
        StringField("mobile"),
        StringField("pan")
    ]

    class Meta:
        model = EmployerLeads

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
            find_res_objects.append(DictToObj(doc))
        return find_res_objects

    async def find_by_pk(self, request: Request, pk):
        find_one_res = self.Meta.model.find_one(
            {"_id": bson.ObjectId(pk)})
        return DictToObj(find_one_res)

    async def create(self, request: Request, data: Dict):
        sales_id = request.state.user.get("sales_id")
        data["sales_id"] = bson.ObjectId(sales_id)

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
