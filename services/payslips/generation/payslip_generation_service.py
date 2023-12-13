from datetime import datetime
import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfWriter, PdfReader

from services.payslips.uploads.payslip_upload_service import PayslipUploadService

from payslips.utils.convert_to_inr import convert_to_inr
from services.ewa.apollo.utils import convert_to_words

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.join(SCRIPT_DIR, '..', '..', '..')
TEMPLATE_PATH = os.path.join(
    PARENT_DIR, "templates/pdf/unipe_payslip_template.pdf")


class PayslipGenerationService:
    def __init__(self, payslip_data):
        self.header = payslip_data["header"]
        self.employee = payslip_data["employee_details"]
        self.salary = payslip_data["attendance_details"]
        self.earnings = payslip_data["earnings"]
        self.deductions = payslip_data["deductions"]
        self.final = payslip_data["final"]

    def _create_header(self, can):
        header = self.header
        header_date_str = header.get("date", "N/A")
        header_datetime = datetime.fromisoformat(
            header_date_str.replace("Z", "+00:00"))
        header_date = header_datetime.strftime("%b %Y").upper()

        can.setFont("Helvetica", 16)
        can.drawString(36, 768, header_date)
        can.setFont("Helvetica", 8)
        can.drawString(36, 750, header.get("company_name", "N/A"))
        can.drawString(36, 735, header.get("company_address", "N/A"))

    def _create_employee_details(self, can):
        employee = self.employee
        can.setFont("Helvetica", 9)
        can.drawString(37, 695, employee.get("employee_name", "N/A"))
        can.setFont("Helvetica", 8)
        can.drawString(36, 660, employee.get("employee_no", "N/A"))
        can.drawString(166, 660, employee.get("date_joined", "N/A"))
        can.drawString(297, 660, employee.get("department", "N/A"))
        can.drawString(428, 660, employee.get("sub_department", "N/A"))
        can.drawString(36, 620, employee.get("designation", "N/A"))
        can.drawString(166, 620, employee.get("pan", "N/A"))
        can.drawString(297, 620, employee.get("uan", "N/A"))

    def _create_salary_details(self, can):
        salary = self.salary
        can.drawString(36, 533, salary.get("actual_payable_days", "N/A"))
        can.drawString(190, 533, salary.get("total_working_days", "N/A"))
        can.drawString(336, 533, salary.get("loss_of_pay_days", "N/A"))
        can.drawString(461, 533, salary.get("days_payable", "N/A"))

    def _create_earning_details(self, can):
        earnings = self.earnings
        can.drawString(258, 480, earnings.get("basic", "N/A"))
        can.drawString(258, 465, earnings.get("hra", "N/A"))
        can.drawString(258, 450, earnings.get("other_allowance", "N/A"))
        can.drawString(258, 415, earnings.get("total_earnings", "N/A"))

    def _create_deduction_details(self, can):
        deductions = self.deductions
        can.drawString(520, 480, deductions.get("tax_deducted", "N/A"))
        can.drawString(520, 465, deductions.get("pf_contribution", "N/A"))
        can.drawString(520, 450, deductions.get("professional_tax", "N/A"))
        can.drawString(520, 435, deductions.get("other_deductions", "N/A"))
        can.drawString(520, 416, deductions.get("total_deductions", "N/A"))

    def _create_final_details(self, can):
        final = self.final
        net_pay = convert_to_inr(final.get('net_pay', 'N/A'))
        net_salary_in_words = convert_to_words(int(final.get("net_pay")[1:]))
        can.drawString(258, 368, f"{net_pay}")
        can.drawString(258, 353, f"{net_salary_in_words}")

    def _create_payslip_overlay(self):
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont("Helvetica", 12)

        self._create_header(can)
        self._create_employee_details(can)
        self._create_salary_details(can)
        self._create_earning_details(can)
        self._create_deduction_details(can)
        self._create_final_details(can)
        can.save()

        packet.seek(0)

        new_pdf = PdfReader(packet)
        return new_pdf

    def generate_payslip(self):
        overlay_pdf = self._create_payslip_overlay()

        existing_pdf = PdfReader(open(TEMPLATE_PATH, "rb"))
        output = PdfWriter()

        for page in existing_pdf.pages:
            page.merge_page(overlay_pdf.pages[0])
            output.add_page(page)

        # ? To write the data to a specific File
        # with open(output_path, "wb") as output_stream:
        #     output.write(output_stream)

        output_stream = io.BytesIO()
        output.write(output_stream)
        output_stream.seek(0)
        return output_stream
