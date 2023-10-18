from dal.models.employees import Employee
from kyc_service.services.ewa.apollo.schema import ApolloLoanPayload
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


def upload_loc_creation_documents(apollo_loan_payload: ApolloLoanPayload):
    Employee.fetch_employees_details(
        {}
    )
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.drawString(10, 100, "Hello world")
    can.save()

    # move to the beginning of the StringIO buffer
    packet.seek(0)

    # create a new PDF with Reportlab
    new_pdf = PdfFileReader(packet)
    # read your existing PDF
    existing_pdf = PdfFileReader(
        open("/home/shubham/Downloads/sanction_letter_and_KFS.pdf", "rb"))
    output = PdfFileWriter()
    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.pages[0]
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)
    # finally, write "output" to a real file
    output_stream = open(
        "/home/shubham/Downloads/sanction_letter_and_KFS_new.pdf", "wb")
    output.write(output_stream)
    output_stream.close()
