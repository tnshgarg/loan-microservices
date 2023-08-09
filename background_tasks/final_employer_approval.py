from background_tasks.background_task import BackgroundTask
from dal.models.employer import Employer


class FinalEmployerApproval(BackgroundTask):

    def run(self, payload):
        # check typecasting
        employer_id: str = payload["employer_id"]
        approve_or_deny: str = payload["approve_or_deny"]

        approval_stage = Employer.ApprovalStage.APPROVED if approve_or_deny == "approve" else Employer.ApprovalStage.DENIED

        # update in db
        employer_update_result = Employer.update_one({
            "_id": employer_id
        }, {
            "$set": {
                "approvalStage": approval_stage
            }
        }, upsert=True)

        self.logger.info("Employer Updated", extra={
            "data": {
                "employer_update_result": {
                    "upserted_id": employer_update_result.upserted_id,
                    "matched_count": employer_update_result.matched_count
                }
            }
        })
