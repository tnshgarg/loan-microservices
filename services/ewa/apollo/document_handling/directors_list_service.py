

from datetime import datetime, timedelta
from io import BytesIO
import os
from bson import ObjectId
from dal.models.employees import Employee

from dal.models.employer import Employer
from dal.models.employments import Employments
from pyhtml2pdf import converter

from services.storage.uploads.pdf_service import PDFService


class DirectorsListService:

    def __init__(self, employer) -> None:
        self.employer = employer

    @classmethod
    def get_row_template(cls, sr_no, employee_name, date_of_birth, designation, current_address, pan_number):
        return (f"""
        <tr>
            <th>{sr_no}.</th>
            <th data-priority="1">{employee_name}</th>
            <th data-priority="2">{date_of_birth}</th>
            <th data-priority="3">{designation}</th>
            <th data-priority="4">{current_address}</th>
            <th data-priority="4">{pan_number}</th>
        </tr>
        """)

    def generate_document(self) -> BytesIO:
        list_of_directors_template = open(
            "templates/html/ewa/list_of_directors.html"
        )
        template_str = list_of_directors_template.read()
        directors = Employee.fetch_employees_details(
            filter_={
                "_id": {"$in": self.employer["commercialLoanDetails"]["promoters"]}
            },
            employments=True,
            governmentIds=True
        )
        table_rows = ""
        for i, director in enumerate(directors):
            table_rows += self.get_row_template(
                sr_no=i+1,
                employee_name=director["employeeName"],
                date_of_birth=director["pan"]["data"]["date_of_birth"],
                designation=director["employments"][-1]["designation"],
                current_address=director["currentAddress"],
                pan_number=director["pan"]["number"]
            )
            print(director)
        list_of_directors_html = template_str.format(
            companyName=self.employer["companyName"],
            tableRows=table_rows
        )
        return PDFService.html_to_pdf(f"{self.employer['_id']}_list_of_directors", list_of_directors_html)
