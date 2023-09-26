from background_tasks.background_task import BackgroundTask
from ops.models.employer_email_payload import EmployerEmailPayload
from services.comms.emailing_service import FileAttachment, GmailService
from services.employer.pending_repayments.email_template_service import \
    EmailTemplateService
from services.employer.pending_repayments.fetch_service import \
    EmployerPendingRepaymentsFetchService
from services.employer.pending_repayments.related_email_ids_service import \
    RelatedEmailIDsService
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
        mail_to_addresses = RelatedEmailIDsService(
            employer_info).fetch_related_email_ids()

        # create email attachment
        csv_columns_map = EmployerPendingRepaymentsFetchService.fetch_csv_columns_map()
        pending_repayments_df = pending_repayments_df.rename(
            columns=csv_columns_map)
        pending_repayments_csv = pending_repayments_df.to_csv(index=False)
        files = [FileAttachment(
            # suggest name
            name=f"pending_repayments_data_{request_date_string}.csv",
            data_binary=pending_repayments_csv
        )]

        # get mail HTML template and subject
        email_template_service = EmailTemplateService(employer_info)
        mail_html_content = email_template_service.fetch_email_template(
            pending_repayments_summary)
        mail_subject = email_template_service.fetch_email_subject()

        # send email to stakeholders
        with GmailService(sender_email=sender_email) as mailing_service:
            mailing_service.sendmail(
                from_name="Employer Notifications",  # suggest name
                to_addresses=mail_to_addresses,
                subject=mail_subject,
                files=files,
                html_blocks=[mail_html_content]
            )
