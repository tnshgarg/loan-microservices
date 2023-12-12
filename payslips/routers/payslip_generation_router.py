import os
from typing import Optional
from typing_extensions import Annotated
from bson import ObjectId

from fastapi import APIRouter, HTTPException
from fastapi import APIRouter, BackgroundTasks, Depends, Form, UploadFile
from background_tasks.payslips.generate_and_upload_payslips import GenerateAndUploadPayslips

from services.payslips.generation.payslip_generation_service import PayslipGenerationService
from services.payslips.uploads.payslip_upload_service import PayslipUploadService
from services.storage.uploads.media_upload_service import MediaUploadService

STAGE = os.environ["STAGE"]
TEMPLATE_PATH = "/Users/tanishgarg/Documents/GitHub/microservices/templates/pdf/unipe_payslip_template.pdf"

payslip_generation_router = APIRouter(
    prefix=f"/generate-payslips",
    tags=["generate-payslips"]
)


def convert_to_objectids(ids):
    try:
        return [ObjectId(str_id) for str_id in ids]
    except Exception as e:
        print(f"Error converting to ObjectId: {e}")
        return None


@payslip_generation_router.post("/")
def generate_payslips(background_tasks: BackgroundTasks, payslipsData: dict):
    """
        To use Payslip Generation Router, pass the payslips data in the following format:

        Payload:
        {
            "payslips": [ObjectId('64ddc25fa4f4ec0089ac780b'), ObjectId('64ddc25fa4f4ec0089ac780c')]
        }
    }
    """
    try:
        # """Generate Payslip"""
        # payslip_service = PayslipGenerationService(payslipData)
        # payslip_fd = payslip_service.generate_payslip()

        # """Upload Payslip to GDrive and S3"""
        # payslip_upload_service = PayslipUploadService(
        #     employment_id=payslipData["employment_details"]["employment_id"])
        # payslip_drive_url = payslip_upload_service.upload_document(
        #     fd=payslip_fd, payslip_data=payslipData)

        converted_payslips_data = convert_to_objectids(
            payslipsData["payslips"])
        handler_payload = {
            "payslips": converted_payslips_data
        }
        background_tasks.add_task(
            GenerateAndUploadPayslips().run, handler_payload)

        return {
            "status": "SUCCESS",
            "message": "Payslips Generated And Uploaded Successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=400, detail="Invalid payslip data format")
