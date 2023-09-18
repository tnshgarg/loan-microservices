from background_tasks.background_task import BackgroundTask
from dal.models.employer import Employer
from ops.models.employer_email_payload import EmployerEmailPayload
from services.comms.emailing_service import FileAttachment, GmailService
from services.employer.pending_repayments_service import \
    EmployerPendingRepaymentsService


class PendingRepaymentsEmail(BackgroundTask):

    def run(self, payload):
        # check typecasting
        employer_info: EmployerEmailPayload = payload["employer_info"]

        # get pending repayments dataframe
        pending_repayments_df = EmployerPendingRepaymentsService(
            employer_info).fetch_pending_repayments()

        # check if no pending repayments
        if pending_repayments_df is None:
            return

        # send mail to tech-ops
        sender_email = "reports@unipe.money"

        # fetch addresses to mail to
        mail_to_addresses = []
        # fetch registrar email
        employer_find_res = Employer.find_one(
            {
                "_id": employer_info.employer_id
            }
        )
        employer_registrar_email = employer_find_res.get(
            "registrar", {}).get("email")
        mail_to_addresses.append(employer_registrar_email)
        # TODO : fetch sm email
        # TODO :fetch rm email
        # fetch internal email
        # unipe_internal_email = "employer-mails@unipe.money"
        # mail_to_addresses.append(unipe_internal_email)

        # create email attachment
        pending_repayments_csv = pending_repayments_df.to_csv(index=False)
        files = [FileAttachment(
            name="pending_repayments_data.csv",  # suggest name
            data_binary=pending_repayments_csv
        )]

        # send email to stakeholders
        with GmailService(sender_email=sender_email) as mailing_service:
            mailing_service.sendmail(
                from_name="Employer Notifications",  # suggest name
                to_addresses=mail_to_addresses,
                subject=f'''Upcoming Pending Repayments Notification ''',  # add date
                message_text=f"""
                        Attached is the list of pending repayments
                    """,
                files=files
            )
