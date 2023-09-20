from background_tasks.background_task import BackgroundTask
from dal.models.employer import Employer
from ops.models.employer_email_payload import EmployerEmailPayload
from ops.templates.repayment_reminder_template import \
    get_repayment_reminder_template
from services.comms.emailing_service import FileAttachment, GmailService
from services.employer.pending_repayments.fetch_service import \
    EmployerPendingRepaymentsFetchService
from services.employer.pending_repayments.summary_service import \
    EmployerPendingRepaymentsSummaryService


class PendingRepaymentsEmail(BackgroundTask):

    def run(self, payload):
        # check typecasting
        employer_info: EmployerEmailPayload = payload["employer_info"]

        # get pending repayments dataframe
        pending_repayments_df = EmployerPendingRepaymentsFetchService(
            employer_info).fetch_pending_repayments()

        # check if no pending repayments
        if pending_repayments_df is None:
            return

        # get pending repayments summary
        pending_repayments_summary = EmployerPendingRepaymentsSummaryService(
            employer_info, pending_repayments_df).fetch_pending_repayments_summary()

        # get request date string
        request_date_string = employer_info.request_date.get_date_string()

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
        # unipe_internal_email = "qa-mails@unipe.money"
        # mail_to_addresses.append(unipe_internal_email)

        # create email attachment
        pending_repayments_csv = pending_repayments_df.to_csv(index=False)
        files = [FileAttachment(
            # suggest name
            name=f"pending_repayments_data_{request_date_string}.csv",
            data_binary=pending_repayments_csv
        )]

        # get mail HTML template
        mail_html_content = get_repayment_reminder_template(
            pending_repayments_summary)

        # send email to stakeholders
        with GmailService(sender_email=sender_email) as mailing_service:
            mailing_service.sendmail(
                from_name="Employer Notifications",  # suggest name
                to_addresses=mail_to_addresses,
                subject=f'''Upcoming Auto-deduction of Unipe Repayments on {request_date_string}''',
                files=files,
                html_blocks=[mail_html_content]
            )
