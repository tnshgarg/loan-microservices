import json
import os

import bson

from background_tasks.background_task import BackgroundTask
from dal.models.employer import Employer
from dal.models.ops_employer_login import OpsEmployerLogins
from dal.models.sales_users import SalesUser
from services.comms.emailing_service import GmailService
from services.comms.html_blocks_service import HTMLBlocksService


class FinalEmployerApproval(BackgroundTask):

    def run(self, payload):
        # check typecasting
        employer_id: str = payload["employer_id"]
        employer_id_trimmed = employer_id.split("-")[-1]
        approve_or_deny: str = payload["approve_or_deny"]

        # fetch ops_employer_login_info from db
        ops_employer_login_info = OpsEmployerLogins.find_one(
            {"employer_id": employer_id}, {"_id": 0})
        company_name = ops_employer_login_info["company_name"]

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

        # if approved, send email to stakeholders otherwise return
        if approval_stage != Employer.ApprovalStage.APPROVED:
            return

        # send mail to tech-ops
        sender_email = "reports@unipe.money"

        # fetch addresses to mail to
        ops_final_approvers = json.loads(
            os.environ.get("OPS_FINAL_APPROVERS", "{}"))
        mail_to_addresses = list(ops_final_approvers.values())

        # fetch sales user email
        sales_id = ops_employer_login_info.get("sales_id")
        sales_id = bson.ObjectId(sales_id)
        sales_user_info = SalesUser.find_one({"_id": sales_id}, {"email": 1})
        sales_user_email = sales_user_info["email"]
        mail_to_addresses.append(sales_user_email)

        with GmailService(sender_email=sender_email) as mailing_service:
            mailing_service.sendmail(
                from_name="Employer Approval Process",
                to_addresses=mail_to_addresses,
                subject=f'''[{employer_id_trimmed}] "{company_name}" Employer Approval Process''',
                message_text=f"""
                        Employer is successfully approved.
                    """,
                html_blocks=HTMLBlocksService.compile_html_blocks(
                    [
                        ("Employer Information Received",
                         ops_employer_login_info),
                        ("Employer Approval Stage",
                         approval_stage),
                    ]
                )
            )
