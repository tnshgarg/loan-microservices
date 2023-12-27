
from functools import lru_cache
from bson import ObjectId
from dal.models.employer import Employer
import cachetools.func


def get_mapped_employer_ids(sales_id):
    employers = Employer.find({
        "salesUsers": {
            "$elemMatch": {
                "salesId": ObjectId(sales_id)
            }
        }
    }, {"_id": 1})
    return [employer["_id"] for employer in employers]


@cachetools.func.ttl_cache(maxsize=128, ttl=60)
def get_related_employers_filter(sales_id, sales_user_type):
    if sales_user_type in ["rm", "sm"]:
        return {"$in": get_mapped_employer_ids(sales_id)}
    else:
        return {"$nin": []}
