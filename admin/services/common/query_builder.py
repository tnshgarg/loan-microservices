
BRANCH_CONDITIONS = {"and", "or"}

OPERATORS = {
    "eq": lambda v: {"$eq": v},
    "neq": lambda v: {"$ne": v},
    "lt": lambda v: {"$lt": v},
    "gt": lambda v: {"$gt": v},
    "le": lambda v: {"$lte": v},
    "ge": lambda v: {"$gte": v},
    "in": lambda v: {"$in": v},
    "not_in": lambda v: {"$nin": v},
    "is_false": lambda v: False,
    "is_true": lambda v: True,
    "is_null": lambda v:  None,
    "is_not_null": lambda f, v: Q(f, None, "ne"),
    "between": lambda v: {"$gte": v[0], "$lte": v[1]},
    "not_between": lambda v: {"$lt": v[0], "$gt": v[1]},
    "startswith": lambda v: {"$regex": f"^{v}"},
    "not_startswith": lambda v: {"$not": {"$regex": f"^{v}"}},
    "endswith": lambda v: {"$regex": f"{v}$"},
    "not_endswith": lambda v: {"$not": {"$regex": f"{v}$"}},
    "contains": lambda v: {"$regex": f"{v}"},
    "not_contains": lambda v: {"$not": {"$regex": f"{v}"}},
}


class QueryBuilderException(Exception):

    def __init__(self, where) -> None:
        super().__init__(f"QueryBuilder Exception for clause: {where}")


def build_query(where):

    if isinstance(where, list):
        return [build_query(clause) for clause in where]
    if isinstance(where, dict):
        query = {}
        for op, value in where.items():
            if op in BRANCH_CONDITIONS:
                query["$" + op] = build_query(value)
            elif op in OPERATORS:
                return OPERATORS[op](value)
            else:
                query[op] = build_query(value)
        return query
    raise QueryBuilderException(where)
