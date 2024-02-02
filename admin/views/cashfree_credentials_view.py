from typing import Any, Dict, List, Optional, Union
from admin.views.admin_view import AdminView
from dal.models.credentials import Credentials
from starlette_admin import StringField, PasswordField
from starlette.requests import Request
from admin.utils import DictToObj
from admin.models.credential import Credential

class CashfreeCredentialsViews(AdminView):
    document = Credential
    identity = "cashfree_credentials"
    name = "Cashfree Credentials"
    label = "Cashfree Credentials"
    icon = "fa fa-users"
    model = Credentials
    pk_attr = "_id"
    fields = [
        StringField("_id"),
        StringField("pId", label="Employer Id"),
        PasswordField("username", label="Username"),
        PasswordField("password", label="Password"),
        PasswordField("publicKey", label="Public Key"),
        StringField("portal"),
    ]

    def is_accessible(self, request: Request) -> bool:
        roles = request.state.user["roles"]
        return "payouts_credentials" in roles

    async def create(self, request: Request, data: Dict):
        res = self.model.put_cashfree_creds(
            employerId=data["pId"], client_id=data["username"], client_secret=data["password"], public_key=data["public_key"])
        upserted_id = res.upserted_id
        data["_id"] = upserted_id
        return DictToObj(data)

    async def find_all(self, request: Request, skip: int = 0, limit: int = 100,
                       where: Union[Dict[str, Any], str, None] = None,
                       order_by: Optional[List[str]] = None) -> List[Any]:
        q = await self._build_query(request, where)
        filter_ = q.to_query(self.document)
        res = self.model.aggregate(pipeline=[
            {'$match': filter_},
            {'$lookup': {
                'from': 'employers',
                'localField': 'pId',
                'foreignField': '_id',
                'as': 'credentials'
            }},
            {"$match":
             {"credentials":
              {"$ne": []}
              }
             }
        ])
        find_all_res = []
        for employer_lead in res:
            find_all_res.append(
                DictToObj(self.model.modify_result(employer_lead)))
        return find_all_res
