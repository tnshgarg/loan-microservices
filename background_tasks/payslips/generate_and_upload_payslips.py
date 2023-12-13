from background_tasks.background_task import BackgroundTask
from dal.models.payslips import Payslips
from background_tasks.payslips.aggregation.get_payslip_info import get_payslip_aggregation_info
from services.payslips.generation.payslip_generation_service import PayslipGenerationService
from services.payslips.uploads.payslip_upload_service import PayslipUploadService


class GenerateAndUploadPayslips(BackgroundTask):

    def run(self, payload):
        # check typecasting
        payslips = payload["payslips"]

        payslips_data = Payslips.aggregate(
            get_payslip_aggregation_info(payslips))

        for payslip_data in payslips_data:
            """Generate Payslips"""
            payslip_gen_service = PayslipGenerationService(payslip_data)
            payslip_fd = payslip_gen_service.generate_payslip()

            """Upload Payslips"""
            payslip_upload_service = PayslipUploadService(
                employment_id=payslip_data["employment_details"]["employment_id"])
            payslip_upload_service.upload_document(
                fd=payslip_fd, payslip_data=payslip_data)
