
EMPLOYEE_DETAILS_FOR_OFFER_PIPELINE = [
    {
        "$lookup": {
            "from": "bankAccounts",
            "localField": "_id",
            "foreignField": "pId",
            "as": "bankAccount",
        },
    },
    {
        "$unwind": {
            "path": "$bankAccount",
            "preserveNullAndEmptyArrays": True,
        }
    },
    {
        "$lookup": {
            "from": "employments",
            "localField": "_id",
            "foreignField": "pId",
            "as": "employment",
        },
    },
    {
        "$addFields": {
            "employment": {
                "$last": "$employment",
            },
        },
    },
    {
        "$lookup": {
            "from": "governmentIds",
            "localField": "_id",
            "foreignField": "pId",
            "as": "governmentIds",
        },
    },
    {
        "$project": {
            "_id": {
                "$toString": "$_id",
            },
            "bankAccount.data.accountHolderName": 1,
            "bankAccount.verifyStatus": 1,
            "employment._id": "$employment._id",
            "employment.active": "$employment.active",
            "employment.employerId": "$employment.employerId",
            "employment.onboarded": "$employment.onboarded",
            "governmentIds.data.name": 1,
            "governmentIds.number": 1,
            "governmentIds.type": 1,
            "governmentIds.verifyStatus": 1,
        }
    },
]
