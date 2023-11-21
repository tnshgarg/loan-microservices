

from datetime import datetime, timedelta
from io import BytesIO
import os
from bson import ObjectId
from dal.models.employees import Employee

from dal.models.employer import Employer
from dal.models.employments import Employments
from pyhtml2pdf import converter

from kyc_service.services.storage.uploads.pdf_service import PDFService


class SalarySlipService:

    def __init__(self, employer_id: str, unipe_employee_id: ObjectId) -> None:
        self.employer_id = employer_id
        self.unipe_employee_id = unipe_employee_id

    @classmethod
    def get_last_salary_slip_date_range(cls):
        this_month = datetime.now().replace(day=1)
        last_day = (this_month - timedelta(days=1)).strftime("%d/%m/%Y")
        first_day = "01"+last_day[2:]
        return first_day, last_day

    def generate_document(self) -> BytesIO:
        salary_slip_template = open("templates/html/ewa/salary_slip.html")
        template_str = salary_slip_template.read()
        employer_details = Employer.find_one({"_id": self.employer_id})
        employment_details = Employments.find_one({
            "pId": self.unipe_employee_id,
            "active": True,
            "employerId": self.employer_id
        })
        employee_details = Employee.find_one({"_id": self.unipe_employee_id})
        first_day, last_day = self.get_last_salary_slip_date_range()
        salary_slip_html = template_str.format(
            employerName=employer_details["companyName"],
            employerPhone=employer_details["registrar"]["mobile"],
            employeeName=employee_details["employeeName"],
            employerEmployeeId=employment_details["employerEmployeeId"],
            monthlyInHandSalary=employment_details.get(
                "mInHandSalary", (float(employment_details["aCTC"].replace(",", ""))/12)),
            previousMonthFirstDay=first_day,
            previousMonthLastDay=last_day
        )
        return PDFService.html_to_pdf(f"{self.unipe_employee_id}_salary_slip", salary_slip_html)
