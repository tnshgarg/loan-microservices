import bson
from typing import Any, Coroutine, Dict, List, Optional, Sequence, Union
from starlette.requests import Request
from starlette_admin import BaseModelView
from admin.services.common.employer_filter import get_related_employers_filter
from admin.services.common.query_builder import build_query
from admin.utils import DictToObj


class AdminView(BaseModelView):

    def is_accessible(self, request: Request) -> bool:
        roles = request.state.user["roles"]
        return "admin" in roles or "super-admin" in roles

    def can_edit(self, request: Request) -> bool:
        return "super-admin" in request.state.user["roles"]

    def can_delete(self, request: Request) -> bool:
        return "super-admin" in request.state.user["roles"]

    def can_create(self, request: Request) -> bool:
        return "super-admin" in request.state.user["roles"]

    def get_employers_filter(self, request: Request) -> Dict[str, Any]:
        return get_related_employers_filter(
            sales_id=request.state.user["sales_id"],
            sales_user_type=request.state.user["sales_user_type"]
        )

    def create_text_search_filter(self, term: Union[str, int, None]) -> Dict[str, Union[str, int]]:
        if term is None or not isinstance(term, (str, int)):
            return {}
        fields_contain = [
            {field.name: {"contains": str(term)}} for field in self.fields if not field.exclude_from_list
        ]
        return build_query({"or": fields_contain})

    def create_complex_filter(self, where: Dict[str, Any]) -> Dict[str, Any]:
        return build_query(where)

    def parse_where_clause(self, where: Union[Dict[str, Any], str, None] = None) -> Dict[str, Any]:
        if where is None:
            return {}
        if isinstance(where, (str, int)):
            return self.create_text_search_filter(where)
        elif isinstance(where, dict):
            return self.create_complex_filter(where)

    def create_sort_key(self, order_by: List[str]) -> List[tuple]:
        return [(field, 1) if sort_order == "asc" else (field, -1) for order_by_op in order_by for field, sort_order in [order_by_op.split()]]

    async def count(self, request: Request, where: Union[Dict[str, Any], str, None] = None) -> int:
        filter_ = self.parse_where_clause(where)
        return len(list(self.model.find(filter_)))

    async def find_all(self, request: Request, skip: int = 0, limit: int = 100,
                       where: Union[Dict[str, Any], str, None] = None,
                       order_by: Optional[List[str]] = None) -> List[Any]:
        filter_ = self.parse_where_clause(where)
        sort_key = self.create_sort_key(order_by)
        res = self.model.find(filter_).sort(sort_key).skip(skip).limit(limit)
        find_all_res = [DictToObj(employer_lead) for employer_lead in res]
        return find_all_res

    async def find_by_pk(self, request: Request, pk: str) -> DictToObj:
        obj_id = bson.ObjectId(pk) if len(pk) == 24 else pk
        res = self.model.find_one({"_id": obj_id})
        return DictToObj(res)

    def parse_pks(self, pks: List[str]) -> List[bson.ObjectId]:
        return [bson.ObjectId(pk[10:34]) for pk in pks if "ObjectId" in pk]

    async def find_by_pks(self, request: Request, pks: List[str]) -> List[DictToObj]:
        object_ids_to_find = {"_id": {"$in": self.parse_pks(pks)}}
        res = self.model.find(object_ids_to_find)
        return [DictToObj(obj) for obj in res]

    async def create(self, request: Request, data: Dict[str, Any]) -> DictToObj:
        inserted_id = self.model.insert_one(data).inserted_id
        data["_id"] = inserted_id
        return DictToObj(data)

    async def edit(self, request: Request, pk: str, data: Dict[str, Any]) -> DictToObj:
        obj_id = bson.ObjectId(pk)
        self.model.update_one(filter_={"_id": obj_id}, update={"$set": data})
        data["_id"] = pk
        return DictToObj(data)
        inserted_id = self.model.insert_one(data).inserted_id

    async def delete(self, request: Request, pks: List[str]) -> Optional[int]:
        object_ids_to_delete = [bson.ObjectId(
            pk[10:34]) for pk in pks if "ObjectId" in pk]
        delete_res = self.model.delete({"_id": {"$in": object_ids_to_delete}})
        return delete_res.deleted_count
