import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfWriter, PdfReader

from payslips.utils.convert_to_inr import convert_to_inr
# from services.ewa.apollo.utils import convert_to_words


ONES = ["", "one", "two", "three", "four",
        "five", "six", "seven", "eight", "nine"]
TEENS = ["ten", "eleven", "twelve", "thirteen", "fourteen",
         "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
TENS = ["", "", "twenty", "thirty", "forty",
        "fifty", "sixty", "seventy", "eighty", "ninety"]


def convert_to_words(num):
    if num == 0:
        return "zero"
    elif num < 0:
        return "minus " + convert_to_words(abs(num))
    elif num < 10:
        return ONES[num]
    elif num < 20:
        return TEENS[num - 10]
    elif num < 100:
        return TENS[num // 10] + (" " + convert_to_words(num % 10) if num % 10 != 0 else "")
    elif num < 1000:
        return ONES[num // 100] + " hundred" + (" and " + convert_to_words(num % 100) if num % 100 != 0 else "")
    elif num < 100000:
        return convert_to_words(num // 1000) + " thousand" + (" " + convert_to_words(num % 1000) if num % 1000 != 0 else "")
    elif num < 10000000:
        return convert_to_words(num // 100000) + " lakh" + (" " + convert_to_words(num % 100000) if num % 100000 != 0 else "")
    elif num < 1000000000:
        return convert_to_words(num // 10000000) + " crore" + (" " + convert_to_words(num % 10000000) if num % 10000000 != 0 else "")
    else:
        return "number out of range"


def convert_to_inr(number):
    s = str(number)
    if len(s) <= 3:
        return s
    else:
        initial = s[:-3]
        last_three = s[-3:]
        formatted_initial = ','.join([initial[i:i+2]
                                     for i in range(0, len(initial), 2)])
        return formatted_initial + ',' + last_three


class PayslipGenerationService:
    def __init__(self, payslip_data):
        self.header = payslip_data["header"]
        self.employee = payslip_data["employee_details"]
        self.salary = payslip_data["salary_details"]
        self.earnings = payslip_data["earnings"]
        self.deductions = payslip_data["deductions"]
        self.final = payslip_data["final"]

    def _create_header(self, can):
        header = self.header
        can.setFont("Helvetica", 16)
        can.drawString(36, 768, header.get("date", "N/A"))
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

    def generate_payslip(self, template_path, output_path):
        overlay_pdf = self._create_payslip_overlay()

        existing_pdf = PdfReader(open(template_path, "rb"))
        output = PdfWriter()

        for page in existing_pdf.pages:
            page.merge_page(overlay_pdf.pages[0])
            output.add_page(page)

        with open(output_path, "wb") as output_stream:
            output.write(output_stream)


# Example usage
payslip_data = {
    "header": {
        "date": "JUL 2022",
        "company_name": "Click-Labs Pvt. Ltd",
        "company_address": "IT Park, Plot No. 16, Sector 22, Panchkula, Haryana, 134109"
    },
    "employee_details": {
        "employee_name": "ANANYA CHAKRABORTY",
        "employee_no": "CL-0111",
        "date_joined": "12 Aug 2019",
        "department": "Product",
        "sub_department": "N/A",
        "designation": "Product Designer",
        "pan": "AOSPC8746D",
        "uan": "100915564037"
    },
    "attendance_details": {
        "actual_payable_days": "31.0",
        "total_working_days": "31.0",
        "loss_of_pays_data": "0.0",
        "days_payable": "31",
    },
    "earnings": {
        "basic": "₹22,917",
        "hra": "₹11,459",
        "other_allowance": "₹11,459",
        "total_earnings": "₹45,835",
    },
    "deductions": {
        "tax_deducted": "0",
        "pf_contribution": "₹2750",
        "professional_tax": "₹200.00",
        "other_deductions": "0",
        "total_deductions": "₹2950",
    },
    "final": {
        "net_pay": "₹2950",
    }
}

service = PayslipGenerationService(payslip_data)
