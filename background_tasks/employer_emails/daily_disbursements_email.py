from datetime import timedelta

from background_tasks.background_task import BackgroundTask
from ops.models.employer_email_payload import EmployerDisbursementsEmailPayload
from ops.templates.disbursements_info.daily_disbursements_summary import \
    get_daily_disbursements_summary_template
from services.comms.emailing_service import FileAttachment, GmailService
from services.employer.disbursements.fetch_service import \
    EmployerDisbursementsFetchService
from services.employer.disbursements.summary_service import \
    EmployerDisbursementsSummaryService
from services.employer.related_email_ids_service import RelatedEmailIDsService


class DailyDisbursementsEmail(BackgroundTask):

    def run(self, payload):
        # check typecasting
        employer_info: EmployerDisbursementsEmailPayload = payload["employer_info"]

        # initialize employer disbursements service
        employer_disbursements_fetch_service = EmployerDisbursementsFetchService(
            employer_info)

        # get daily disbursements dataframe
        daily_disbursements_df = employer_disbursements_fetch_service.fetch_daily_disbursements()

        # check if no daily disbursements
        if daily_disbursements_df is None:
            return

        # get monthly disbursements dataframe
        monthly_disbursements_df = employer_disbursements_fetch_service.fetch_monthly_disbursements()

        # get daily disbursements summary
        daily_disbursements_summary = EmployerDisbursementsSummaryService(
            employer_info, daily_disbursements_df).fetch_daily_disbursements_summary()

        # get current date string
        current_date = employer_info.request_date+timedelta(days=1)
        current_date_string = current_date.strftime("%d/%m/%Y")
        current_month = current_date.month

        # send mail to tech-ops
        sender_email = "reports@unipe.money"

        # fetch addresses to mail to
        mail_to_addresses = RelatedEmailIDsService(
            employer_info).fetch_related_email_ids()

        # create email attachments
        csv_columns_map = EmployerDisbursementsFetchService.fetch_csv_columns_map()

        daily_disbursements_df = daily_disbursements_df.drop(
            "unipeEmployeeId", axis=1)
        daily_disbursements_df = daily_disbursements_df.rename(
            columns=csv_columns_map)
        daily_disbursements_csv = daily_disbursements_df.to_csv(index=False)

        monthly_disbursements_df = monthly_disbursements_df.rename(
            columns=csv_columns_map)
        monthly_disbursements_csv = monthly_disbursements_df.to_csv(
            index=False)

        files = [
            FileAttachment(
                name=f"Detailed_Disbursement_{current_date_string}.csv",
                data_binary=daily_disbursements_csv
            ),
            FileAttachment(
                name=f"Monthly_Disbursement_Summary_{current_month}.csv",
                data_binary=monthly_disbursements_csv
            )
        ]

        # get mail HTML template and subject
        mail_html_content = get_daily_disbursements_summary_template(
            daily_disbursements_summary)
        mail_subject = "Unipe Daily Disbursement Update 📣"

        # send email to stakeholders
        with GmailService(sender_email=sender_email) as mailing_service:
            mailing_service.sendmail(
                from_name="Employer Notifications",  # suggest name
                to_addresses=mail_to_addresses,
                subject=mail_subject,
                files=files,
                html_blocks=[mail_html_content]
            )
