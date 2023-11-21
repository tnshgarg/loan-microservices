from PyPDF2 import PdfWriter, PdfReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


class DocumentSigningService:

    def __init__(self, offer_doc) -> None:
        signature = offer_doc["signature"]
        self.borrower_name = signature["borrowerName"]
        self.timestamp = signature["timestamp"].isoformat()
        self.device_name = signature["deviceName"]
        self.device_id = signature["deviceId"]
        self.ip_address = signature["ipAddress"]

    def generate_first_page(self):
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont("Helvetica-Bold", 20)
        can.drawString(30, 700, f"Digitally Signed by {self.borrower_name}")
        can.drawString(30, 670, f"Terms Accepted at {self.timestamp}")
        can.drawString(30, 640, f"IP Address: {self.ip_address}")
        can.drawString(30, 610, f"Device ID: {self.device_id}")
        can.drawString(30, 580, f"Device: {self.device_name}")
        can.save()

        packet.seek(0)
        first_page_pdf = PdfReader(packet)
        return first_page_pdf.pages[0]

    def generate_footer(self):
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont("Helvetica", 10)
        can.line(30, 35, 565, 35)
        can.drawString(30, 25, f"Digitally Signed by {self.borrower_name}")
        can.drawString(300, 25, f"Terms Accepted at {self.timestamp}")
        can.drawString(30, 15, f"IP Address: {self.ip_address}")
        can.drawString(300, 15, f"Device ID: {self.device_id}")
        can.drawString(30, 5, f"Device: {self.device_name}")
        can.save()

        # move to the beginning of the StringIO buffer
        packet.seek(0)

        # create a new PDF with Reportlab
        footer_pdf = PdfReader(packet)
        return footer_pdf.pages[0]

    def sign_pdf(self, pdf_fd) -> io.BytesIO:
        signed_document = PdfWriter()
        pdf_fd.seek(0)

        document = PdfReader(pdf_fd)
        first_page = self.generate_first_page()
        footer = self.generate_footer()
        signed_document.add_page(first_page)
        for page in document.pages:
            page.merge_page(footer)
            signed_document.add_page(page)
        output_stream = io.BytesIO()
        signed_document.write(output_stream)
        output_stream.seek(0)
        return output_stream
