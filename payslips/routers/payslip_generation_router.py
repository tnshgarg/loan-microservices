import os
from typing import Optional
from typing_extensions import Annotated

from fastapi import APIRouter, HTTPException
from fastapi import APIRouter, BackgroundTasks, Depends, Form, UploadFile

from services.payslips.generation.payslip_generation_service import PayslipGenerationService
from services.payslips.uploads.payslip_upload_service import PayslipUploadService
from services.storage.uploads.media_upload_service import MediaUploadService

# Get environment variables
STAGE = os.environ["STAGE"]
TEMPLATE_PATH = "/Users/tanishgarg/Documents/GitHub/microservices/templates/pdf/unipe_payslip_template.pdf"

payslip_generation_router = APIRouter(
    prefix=f"/generate-payslips",
    tags=["generate-payslips"]
)


@payslip_generation_router.get("/ping")
def ping():
    return {
        "status": "success",
        "message": "pong",
    }


@payslip_generation_router.post("/")
def generate_payslips(
    background_tasks: BackgroundTasks,
    payslip_data: dict,
    employmentId: Annotated[str, Form()],
    month: Annotated[str, Form()],
    year: Annotated[str, Form()],
):

    try:
        header = payslip_data.get("header", {})
        employee_details = payslip_data.get("employee_details", {})
        attendance_details = payslip_data.get("attendance_details", {})
        earnings = payslip_data.get("earnings", {})
        deductions = payslip_data.get("deductions", {})
        final = payslip_data.get("final", {})
        payslip_data = {header, employee_details,
                        attendance_details, earnings, deductions, final}

        payslip_service = PayslipGenerationService(payslip_data)
        payslip_service.generate_payslip(
            template_path=TEMPLATE_PATH, output_path=f"{employmentId}-{month}-{year}")

        """Upload Payslips to GDrive and S3"""
        payslip_upload_service = PayslipUploadService(
            employment_id=employmentId)

        # payslip_upload_service.upload_document(file_name=f"", doc.file, doc.content_type)
        with open(LOCAL_FILE_PATH, "rb") as local_file:
            payslip_upload_service.upload_document(
                file_name="your_uploaded_file_name.pdf", file=local_file)

        return {
            "status": "SUCCESS",
            "message": "employer approval triggered"
        }
    except Exception as e:
        raise HTTPException(
            status_code=400, detail="Invalid payslip data format")
