import json
from typing import Any, Dict, List, Optional, Sequence, Type, Union
from starlette.requests import Request
from starlette_admin import BaseModelView
import bson
from admin.services.common.query_builder import build_query
from admin.utils import DictToObj


class AdminView(BaseModelView):
    def is_accessible(self, request: Request) -> bool:
        return "admin" in request.state.user["roles"]

    def create_text_search_filter(self, term):
        filter_ = {}
        if term is None or not isinstance(term, (str, int)):
            return filter_
        fields_contain = []
        for field in self.fields:
            if not field.exclude_from_list:
                fields_contain.append({
                    field.name: {"contains": str(term)}
                })
        return build_query({"or": fields_contain})

    def create_complex_filter(self, where):
        return build_query(where)

    def parse_where_clause(self, where: Union[Dict[str, Any], str, None] = None):
        if where is None:
            return {}
        if isinstance(where, (str, int)):
            return self.create_text_search_filter(where)
        elif isinstance(where, dict):
            return self.create_complex_filter(where)

    def create_sort_key(self, order_by: List[str]):
        sort_list = []
        for order_by_op in order_by:
            field, sort_order = order_by_op.split()
            if sort_order == "asc":
                sort_list.append((field, 1))
            else:
                sort_list.append((field, -1))
        return sort_list

    async def count(self, request: Request, where: Union[Dict[str, Any], str, None] = None) -> int:
        filter_ = {}
        if isinstance(where, str):
            filter_ = self.create_text_search_filter(where)
        res = self.model.find(filter_)
        return len(list(res))

    async def find_all(self, request: Request, skip: int = 0, limit: int = 100,
                       where: Union[Dict[str, Any], str, None] = None,
                       order_by: Optional[List[str]] = None) -> List[Any]:
        filter_ = self.parse_where_clause(where)
        res = self.model.find(filter_)
        res.skip(skip).limit(limit)
        # TODO: integrate `order_by`
        find_all_res = []
        for employer_lead in res:
            find_all_res.append(DictToObj(employer_lead))
        return find_all_res

    async def find_by_pk(self, request: Request, pk):
        if len(pk) == 24:
            res = self.model.find_one({"_id": bson.ObjectId(pk)})
        else:
            res = self.model.find_one({"_id": pk})
        return DictToObj(res)

    def parse_pks(self, pks):
        parsed_pks = []
        for pk in pks:
            if "ObjectId" in pk:
                oid_idx = pk.index("ObjectId")
                pk = pk[oid_idx+10:oid_idx+34]
            else:
                continue
            parsed_pks.append(pk)
        return [bson.ObjectId(pk) for pk in parsed_pks]

    async def find_by_pks(self, request: Request, pks: List[Any]) -> Sequence[Any]:

        res = self.model.find(
            {"_id": {"$in": self.parse_pks(pks)}})
        return [DictToObj(obj) for obj in res]

    async def create(self, request: Request, data: Dict):
        res = self.model.insert_one(data)
        inserted_id = res.inserted_id
        data["_id"] = inserted_id
        return DictToObj(data)

    async def edit(self, request: Request, pk, data: Dict):
        update_res = self.model.update_one(
            filter_={"_id": bson.ObjectId(pk)},
            update={"$set": data}
        )
        data["_id"] = pk
        return DictToObj(data)

    async def delete(self, request: Request, pks: List[Any]) -> Optional[int]:
        object_ids_to_delete = [bson.ObjectId(pk) for pk in pks]
        delete_res = self.model.delete({
            "_id": {
                "$in": object_ids_to_delete
            }
        })
        deleted_document_count = delete_res.deleted_count
        return deleted_document_count
