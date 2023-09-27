from dal.models.employer import Employer
from ops.models.employer_email_payload import RepaymentsEmployerEmailPayload


class RelatedEmailIDsService:

    def __init__(self, employer_info: RepaymentsEmployerEmailPayload) -> None:
        self.employer_info = employer_info

    def _get_aggregation_pipeline(self):
        pipeline = [
            {
                "$match": {
                    "_id": self.employer_info.employer_id
                }
            },
            {
                "$lookup": {
                    "from": "sales_users",
                    "localField": "salesUsers.salesId",
                    "foreignField": "_id",
                    "as": "salesUsersCompleteInfo"
                }
            },
            {
                "$project": {
                    "registrarEmail": "$registrar.email",
                    "salesUsersEmail": "$salesUsersCompleteInfo.email"
                }
            }
        ]

        return pipeline

    def fetch_related_email_ids(self):
        # perform aggregation query
        pipeline = self._get_aggregation_pipeline()
        aggregation_res = Employer.aggregate(pipeline)
        aggregation_res_list = list(aggregation_res)

        related_email_ids = []

        if len(aggregation_res_list):
            employer_res = aggregation_res_list[0]

            registrar_email = employer_res.get("registrarEmail")
            sales_users_email = employer_res.get("salesUsersEmail")

            # comment these out
            # related_email_ids.append(registrar_email)
            # related_email_ids += sales_users_email

        # rename to prod mails
        unipe_internal_email = "prachir@unipe.money"
        related_email_ids.append(unipe_internal_email)

        return related_email_ids
