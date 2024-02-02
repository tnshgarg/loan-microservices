

from admin.services.commercial_loan_details.queries import \
    COMMERCIAL_LOANS_VIEW_AGGREGATE_PIPELINE, \
    COMMERCIAL_LOANS_VIEW_DEFAULT_FILTERS
from dal.models.employer import Employer
from dal.models.encrypted_government_ids import EncryptedGovernmentIds
from kyc.config import Config
from services.storage.uploads.s3_upload_service import S3UploadService


class CommercialLoanDetailsModel:

    @classmethod
    def find(self, filter_=None, skip=0, limit=10, sort=[("_id", 1)]):
        filters = []
        if filter_ is not None:
            filters.append({
                "$match": filter_
            })
        return Employer.aggregate(
            filters +
            COMMERCIAL_LOANS_VIEW_DEFAULT_FILTERS +
            COMMERCIAL_LOANS_VIEW_AGGREGATE_PIPELINE + [
                {
                    '$skip': skip
                }, {
                    '$limit': limit
                }, {
                    "$sort": {
                        k: v for k, v in sort
                    }
                }
            ]
        )

    @classmethod
    def count(self, filter_):
        return len(list(self.find(filter_, limit=10000000)))

    @classmethod
    def find_one(self, filter_=None):
        employer_s3_service = S3UploadService(
            bucket=f"{Config.STAGE}-unipe-employer-final"
        )
        matched_employers = list(self.find(filter_, limit=1))
        if len(matched_employers):
            employer = matched_employers[0]
            government_ids = EncryptedGovernmentIds.find(
                {
                    "pId": {"$in": [promoter["_id"] for promoter in employer["promoters"]]},
                    "provider": "karza"
                })
            government_id_map = {}
            for government_id in government_ids:
                if government_id["pId"] not in government_id_map:
                    government_id_map[government_id["pId"]] = {}
                government_id_map[government_id["pId"]
                                  ][government_id["type"]] = government_id
            promoters_collection_field = []
            for promoter in employer["promoters"]:
                promoters_collection_field.append({
                    "employee": {
                        "_id": promoter["_id"],
                        "_meta": {
                            "repr": f'{promoter["employeeName"]}[{promoter["_id"]}]'
                        }
                    },
                    "currentAddress": promoter.get("currentAddress"),
                    "aadhaar": government_id_map.get(promoter["_id"], {}).get("aadhaar", {}).get("number"),
                    "pan": government_id_map.get(promoter["_id"], {}).get("pan", {}).get("number"),
                    "key_promoter": promoter["_id"] == employer["keyPromoter"],
                })
            employer["promoters"] = promoters_collection_field
            for key, value in employer["documents"]["s3"].items():
                employer["documents"][key] = {
                    "url": employer_s3_service.get_presigned_url(
                        value,
                        use_stage=False
                    ),
                    "filename": value.split("/")[-1]
                }
            return employer
        return None
