

from datetime import datetime
import os
from background_tasks.employer_emails.pending_repayments_email import PendingRepaymentsEmail
from dal.models.db_manager import DBManager
from ops.models.employer_email_payload import EmployerDisbursementsEmailPayload


def test_repayment_email():
    DBManager.init(stage=os.getenv('STAGE'), asset="microservices-tests")
    PendingRepaymentsEmail().run({
        "employer_info": EmployerDisbursementsEmailPayload(
            employerId="c4a9e83d-b734-40ac-9ef2-d2aea9c860d0",
            requestDate=datetime.fromisoformat("2023-12-05"))
    })
