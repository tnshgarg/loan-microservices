

from datetime import datetime
import pytz
import requests
from kyc.config import Config


class ApolloLoanApplicationHook:

    class Action:
        LOC = "LOC"
        DISBURSEMENT = "DISBURSEMENT"

    class Status:
        CREATE = "CREATE"
        DOCUMENTS_UPLOADED = "DOCUMENTS_UPLOADED"
        PENDING = "INPROGRESS"
        PENDING = "SUCCESS"

    def __init__(self, unipe_employee_id, offer_id) -> None:
        self.api_url = Config.APOLLO_LOAN_APPLICATION_HOOK
        self.unipe_employee_id = unipe_employee_id
        self.offer_id = offer_id

    @property
    def debounce_timestamp(self):
        return datetime.now().astimezone(pytz.timezone('Asia/Kolkata')).isoformat()[:-10]

    def post_event(self, action, status):
        response = requests.post(
            url=self.api_url,
            json={
                "unipeEmployeeId": str(self.unipe_employee_id),
                "offerId": str(self.offer_id),
                "action": action,
                "status": status,
                "ts": self.debounce_timestamp
            }
        )
        return response.status_code == 200
