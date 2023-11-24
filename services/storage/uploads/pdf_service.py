from io import BytesIO
import os
from PyPDF2 import PdfWriter, PdfReader
from pyhtml2pdf import converter
from dal.logger import get_app_logger
from kyc.util import app_logger


class PDFService:

    @staticmethod
    def combine_pdfs(pdf_fds: list):
        combined_pdf = PdfWriter()
        for pdf_fd in pdf_fds:
            pdf_file = PdfReader(pdf_fd)
            for page in pdf_file.pages:
                combined_pdf.add_page(page)
        output_stream = BytesIO()
        combined_pdf.write(output_stream)
        output_stream.seek(0)
        return output_stream

    @staticmethod
    def html_to_pdf(file_identifier: str, html: str) -> BytesIO:
        html_file_path = f"/tmp/{file_identifier}.html"
        pdf_file_path = f"/tmp/{file_identifier}.pdf"
        try:
            open(html_file_path, "w").write(html)
            converter.convert(
                f'file://{html_file_path}',
                pdf_file_path,
                install_driver=False
            )
            pdf_document = BytesIO(
                initial_bytes=open(
                    pdf_file_path, "rb"
                ).read()
            )
            return pdf_document
        except Exception as e:
            app_logger.error(msg="Error while printing file", exc_info=e)
        finally:
            if os.path.exists(html_file_path):
                os.remove(html_file_path)
            if os.path.exists(pdf_file_path):
                os.remove(pdf_file_path)
