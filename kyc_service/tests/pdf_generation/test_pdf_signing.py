from PyPDF2 import PdfWriter, PdfReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


def create_first_page():
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica-Bold", 20)
    can.drawString(30, 700, "Digitally Signed by {panName}")
    can.drawString(30, 670, "Terms Accepted at {dateTime}")
    can.drawString(30, 640, "Device: {deviceName}")
    can.drawString(30, 610, "Device ID: {deviceId}")
    can.drawString(30, 580, "IP Address: {ipAddress}")
    can.save()

    # move to the beginning of the StringIO buffer
    packet.seek(0)

    # create a new PDF with Reportlab
    new_pdf = PdfReader(packet)
    return new_pdf


def create_footer():
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica", 12)
    can.line(30, 120, 565, 120)
    can.drawString(30, 100, "Digitally Signed by {panName}")
    can.drawString(300, 100, "Terms Accepted at {dateTime}")
    can.drawString(30, 80, "Device: {deviceName}")
    can.drawString(300, 80, "Device ID: {deviceId}")
    can.drawString(30, 60, "IP Address: {ipAddress}")
    can.save()

    # move to the beginning of the StringIO buffer
    packet.seek(0)

    # create a new PDF with Reportlab
    new_pdf = PdfReader(packet)
    return new_pdf


def test_pdf_signing():

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica", 20)
    can.line(30, 80, 565, 80)
    can.drawString(30, 100, "Hello world")
    can.drawString(30, 110, "Hello world")
    can.drawString(30, 130, "Hello world")
    can.save()

    # move to the beginning of the StringIO buffer
    packet.seek(0)

    # create a new PDF with Reportlab
    new_pdf = PdfReader(packet)
    # read your existing PDF
    existing_pdf = PdfReader(
        open("/home/shubham/Downloads/sanction_letter_and_KFS.pdf", "rb"))
    output = PdfWriter()
    # add the "watermark" (which is the new pdf) on the existing page

    output.add_page(create_first_page().pages[0])
    footer = create_footer()
    for page in existing_pdf.pages:
        page.merge_page(footer.pages[0])
        output.add_page(page)
    # finally, write "output" to a real file
    output_stream = open(
        "/home/shubham/Downloads/sanction_letter_and_KFS_signed.pdf", "wb")
    output.write(output_stream)
    output_stream.close()
