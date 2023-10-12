import json
import os

import bson

from background_tasks.background_task import BackgroundTask
from dal.models.employer import Employer
from dal.models.ops_employer_login import OpsEmployerLogins
from dal.models.sales_users import SalesUser
from services.comms.emailing_service import FileAttachment, GmailService
from services.comms.html_blocks_service import HTMLBlocksService


class SendForFinalApproval(BackgroundTask):

    def run(self, payload):
        # check typecasting
        employer_id: str = payload["employer_id"]
        employer_id_trimmed = employer_id.split("-")[-1]

        # fetch ops_employer_login_info from db
        ops_employer_login_info = OpsEmployerLogins.find_one(
            {"employer_id": employer_id}, {"_id": 0})
        company_name = ops_employer_login_info["company_name"]

        # fetch sales user details from db
        sales_user_id = bson.ObjectId(ops_employer_login_info["sales_id"])
        sales_user_info = SalesUser.find_one(
            {
                "_id": sales_user_id
            },
            {
                "_id": 0,
                "name": 1,
                "email": 1
            }
        )

        # set approval stage as pending in employers collection
        employer_update_result = Employer.update_one({
            "_id": employer_id
        }, {
            "$set": {
                "approvalStage": Employer.ApprovalStage.PENDING
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

        # send mail to tech-ops
        sender_email = "reports@unipe.money"

        # fetch addresses to mail to
        ops_final_approvers = json.loads(
            os.environ.get("OPS_FINAL_APPROVERS", "{}"))
        mail_to_addresses = list(ops_final_approvers.values())

        # extract extra fields from payload
        notes = payload["notes"]
        files = [FileAttachment(name=current_file.filename, data_binary=current_file.file.read(
        )) for current_file in payload["files"]]

        with GmailService(sender_email=sender_email) as mailing_service:
            mailing_service.sendmail(
                from_name="Employer Approval Process",
                to_addresses=mail_to_addresses,
                subject=f'''[{employer_id_trimmed}] "{company_name}" Employer Approval Process''',
                message_text=f"""
                        Approval request for a new employer
                    """,
                html_blocks=HTMLBlocksService.compile_html_blocks(
                    [
                        ("Employer Information Received",
                         ops_employer_login_info),
                        ("Sales User Information",
                         sales_user_info),
                        ("Additional Notes by RM",
                         notes),
                    ],
                    [
                        ("Approve or Deny",
                         f"{self.ops_microservice_url}/approve?employer_id={employer_id}",
                         "SkyBlue")
                    ]
                ),
                files=files
            )
