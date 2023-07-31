from background_tasks.background_task import BackgroundTask
from ops.models.cognito_sign_up import CognitoSignUp
from services.emailing_service import GmailService
from services.html_blocks_service import HTMLBlocksService


class TriggerEmployerApproval(BackgroundTask):

    def run(self, payload):
        # check typecasting
        cognito_sign_up_info: CognitoSignUp = payload["cognito_sign_up_info"]
        company_name = cognito_sign_up_info.company_name
        employer_id = cognito_sign_up_info.employer_id
        employer_id_trimmed = cognito_sign_up_info.employer_id.split("-")[-1]

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
                        Received following information regarding new employer onboarding
                    """,
                html_blocks=HTMLBlocksService.compile_html_blocks(
                    [
                        ("Employer Information Received",
                         cognito_sign_up_info.model_dump()),
                    ],
                    [
                        ("Send for Approval",
                         f"{self.ops_microservice_url}/start?employer_id={employer_id}",
                         "SkyBlue")
                    ]
                )
            )
