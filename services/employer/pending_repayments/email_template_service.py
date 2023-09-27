from dal.models.employer import Employer
from ops.models.employer_email_payload import RepaymentsEmployerEmailPayload
from ops.templates.repayments_reminder.auto_deduction import \
    get_repayments_auto_deduction_template
from ops.templates.repayments_reminder.deduction_at_source import \
    get_repayments_deduction_at_source_template
from services.employer.pending_repayments.utils import get_employer_ewa_type


class EmailTemplateService:

    def __init__(self, employer_info: RepaymentsEmployerEmailPayload) -> None:
        self.employer_info = employer_info
        self.employer_ewa_type = get_employer_ewa_type(
            employer_info.employer_id)

    def _get_ewa_type_template_map(self):
        return {
            Employer.EwaType.AUTO_DEDUCTION: get_repayments_auto_deduction_template,
            Employer.EwaType.DEDUCTION_AT_SOURCE: get_repayments_deduction_at_source_template
        }

    def _get_ewa_type_email_subject_map(self):
        request_date_string = self.employer_info.request_date.get_date_string()
        return {
            Employer.EwaType.AUTO_DEDUCTION: f"Upcoming Auto-deduction of Unipe Repayments on {request_date_string}",
            Employer.EwaType.DEDUCTION_AT_SOURCE: f"Unipe Repayment Alert: Action Required by {request_date_string}"
        }

    def fetch_email_template(self, pending_repayments_summary):
        ewa_type_template_map = self._get_ewa_type_template_map()
        get_repayments_template = ewa_type_template_map[self.employer_ewa_type]

        return get_repayments_template(pending_repayments_summary)

    def fetch_email_subject(self):
        ewa_type_email_subject_map = self._get_ewa_type_email_subject_map()
        email_subject = ewa_type_email_subject_map[self.employer_ewa_type]

        return email_subject
