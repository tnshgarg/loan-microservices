from typing import Any, Dict, List, Optional, Type, Union
from starlette.requests import Request
from starlette_admin import BaseModelView
import bson
from admin.utils import DictToObj


class AdminView(BaseModelView): 
    
    async def count(self, request: Request, where: Union[Dict[str, Any], str, None] = None) -> int:
        filter_ = where or {}
        res = self.model.find(filter_)
        return len(list(res))
    
    async def find_all(self, request: Request, skip: int = 0, limit: int = 100,
                       where: Union[Dict[str, Any], str, None] = None,
                       order_by: Optional[List[str]] = None) -> List[Any]:
        
        # Retrieve userType, if he is SM, RM, or Manager from request.session
        # username = request.session.get("username", None)
        # if username:
        #     user_data = self.model.find_one({"email": username})
        #     if user_data:
        #         userType = user_data.get("type")

        # create a roleChecker Method, through which we can show only specific data to the user type, suppose, if he is a 

        res = self.model.find({})
        res.skip(skip).limit(limit)
        order_by
        find_all_res = []
        for employer_lead in res:
            find_all_res.append(DictToObj(employer_lead))
        return find_all_res
    
    
    async def find_by_pk(self, request: Request, pk):
        res = self.model.find_one({"_id": pk})
        return DictToObj(res)

    
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