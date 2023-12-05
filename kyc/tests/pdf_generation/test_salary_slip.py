from dal.models.db_manager import DBManager
from bson import ObjectId

from services.ewa.apollo.document_handling.salary_slip_service import SalarySlipService


def test_salary_slip():
    DBManager.init(stage="prod")
    print(SalarySlipService(
        employer_id="c4a9e83d-b734-40ac-9ef2-d2aea9c860d0",
        unipe_employee_id=ObjectId("6377939f89f886a21c410d91")
    ).generate_document())
