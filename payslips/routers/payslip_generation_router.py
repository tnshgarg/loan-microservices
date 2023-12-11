import os
from typing import Optional
from typing_extensions import Annotated

from fastapi import APIRouter, HTTPException
from fastapi import APIRouter, BackgroundTasks, Depends, Form, UploadFile

from services.payslips.generation.payslip_generation_service import PayslipGenerationService
from services.payslips.uploads.payslip_upload_service import PayslipUploadService
from services.storage.uploads.media_upload_service import MediaUploadService

STAGE = os.environ["STAGE"]
TEMPLATE_PATH = "/Users/tanishgarg/Documents/GitHub/microservices/templates/pdf/unipe_payslip_template.pdf"

payslip_generation_router = APIRouter(
    prefix=f"/generate-payslips",
    tags=["generate-payslips"]
)


@payslip_generation_router.post("/")
def generate_payslips(payslipData: dict):
    """
        To use Payslip Generation Router, pass the payslips data in the following format:

        {
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
                "days_payable": "31"
            },
            "earnings": {
                "basic": "₹22,917",
                "hra": "₹11,459",
                "other_allowance": "₹11,459",
                "total_earnings": "₹45,835"
            },
            "deductions": {
                "tax_deducted": "0",
                "pf_contribution": "₹2750",
                "professional_tax": "₹200.00",
                "other_deductions": "0",
                "total_deductions": "₹2950"
            },
            "final": {
                "net_pay": "₹2950"
            },
            "employment_details": {
                "employment_id": "abc"
            }
    }
    """
    try:
        """Generate Payslip"""
        payslip_service = PayslipGenerationService(payslipData)
        payslip_fd = payslip_service.generate_payslip()

        """Upload Payslip to GDrive and S3"""
        payslip_upload_service = PayslipUploadService(
            employment_id=payslipData["employment_details"]["employment_id"])
        payslip_drive_url = payslip_upload_service.upload_document(
            fd=payslip_fd, payslip_data=payslipData)

        if (payslip_drive_url != None):
            return {
                "status": "SUCCESS",
                "message": "employer approval triggered"
            }
        else:
            raise Exception("File could not be uploaded")

    except Exception as e:
        raise HTTPException(
            status_code=400, detail="Invalid payslip data format")
