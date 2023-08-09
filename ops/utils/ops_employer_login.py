from dal.models.employer import Employer
from dal.models.ops_employer_login import OpsEmployerLogins


def get_ops_employer_login_info(employer_id):
    # fetch ops_employer_login_info from db
    ops_employer_login_info = OpsEmployerLogins.find_one(
        {"employer_id": employer_id}, {"_id": 0})

    return ops_employer_login_info


def get_all_pending_ops_employer_login_info():
    # fetch all ops_employer_login_info for all pending employer
    pipeline = [
        {
            "$match": {
                "approvalStage": Employer.ApprovalStage.PENDING
            }
        },
        {
            "$lookup": {
                "from": "opsEmployerLogins",
                "as": "opsEmployerLoginInfo",
                "let": {
                    "employerId": "$_id"
                },
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$eq": ["$$employerId", "$employer_id"]
                            }
                        }
                    },
                    {
                        "$sort": {
                            "_id": -1
                        }
                    },
                    {
                        "$limit": 1
                    },
                    {
                        "$project": {
                            "_id": 0
                        }
                    }
                ]
            }
        },
        {
            "$unwind": {
                "path": "$opsEmployerLoginInfo",
                "preserveNullAndEmptyArrays": False
            }
        },
        {
            "$project": {
                "_id": 0,
                "opsEmployerLoginInfo": 1
            }
        }
    ]

    cursor = Employer.aggregate(pipeline)

    all_pending_ops_employer_login_info = []
    for document in cursor:
        all_pending_ops_employer_login_info.append(
            document["opsEmployerLoginInfo"])

    return all_pending_ops_employer_login_info
