from background_tasks.background_task import BackgroundTask
from dal.models.ops_employer_login import OpsEmployerLogins
from services.emailing_service import GmailService
from services.html_blocks_service import HTMLBlocksService


class StartEmployerApproval(BackgroundTask):

    def run(self, payload):
        # check typecasting
        employer_id: str = payload["employer_id"]
        employer_id_trimmed = employer_id.split("-")[-1]

        # fetch ops_employer_login_info from db
        ops_employer_login_info = OpsEmployerLogins.find_one(
            {"employer_id": employer_id}, {"_id": 0})
        company_name = ops_employer_login_info["company_name"]

        # send mail to tech-ops
        sender_email = "reports@unipe.money"
        mail_to_addresses = ("prachir@unipe.money")

        with GmailService(sender_email=sender_email) as mailing_service:
            mailing_service.sendmail(
                from_name=f"Employer Approval Process",
                to_name=f"Unipe Team",
                to_addresses=mail_to_addresses,
                subject=f'''[{employer_id_trimmed}] "{company_name}" Employer Approval Process''',
                message_text=f"""
                        Approval request for a new employer
                    """,
                html_blocks=HTMLBlocksService.compile_html_blocks(
                    [
                        ("Employer Information Received",
                         ops_employer_login_info),
                    ],
                    [
                        ("Approve",
                         f"{self.ops_microservice_url}/approve?employer_id={employer_id}",
                         "Green"),
                        ("Deny",
                         f"{self.ops_microservice_url}/deny?employer_id={employer_id}",
                         "Red")
                    ]
                )
            )
