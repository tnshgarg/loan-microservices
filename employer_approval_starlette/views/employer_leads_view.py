from typing import Any, Dict, Iterable, List, Optional, Union

from starlette.requests import Request
from starlette_admin import BaseModelView, StringField

from dal.models.employer_leads import EmployerLeads
from employer_approval_starlette.utils import DictToObj


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

    async def count(self, request: Request, where: Union[Dict[str, Any], str, None] = None) -> int:
        filter_ = {}
        if where is not None:
            filter_ = where
        employer_leads_res = EmployerLeads.find(filter_)
        return len(list(employer_leads_res))

    async def find_all(self, request: Request, skip: int = 0, limit: int = 100,
                       where: Union[Dict[str, Any], str, None] = None,
                       order_by: Optional[List[str]] = None) -> List[Any]:
        employer_leads_res = EmployerLeads.find({})
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
