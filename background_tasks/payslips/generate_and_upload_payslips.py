from datetime import datetime
from background_tasks.background_task import BackgroundTask
from dal.models.cms import CMS
from dal.models.payslips import Payslips
from background_tasks.payslips.aggregation.get_payslip_info import get_payslip_aggregation_info
from services.payslips.generation.payslip_generation_service import PayslipGenerationService
from services.payslips.uploads.payslip_upload_service import PayslipUploadService


class GenerateAndUploadPayslips(BackgroundTask):

    def cms_payslip_builder(self, payslip_data: dict, asset_url: str):
        existing_content = list(CMS.fetch_content(
            groups=[payslip_data["unipeEmployeeId"]]))

        if len(existing_content):
            existing_content = existing_content[0]
        else:
            existing_content = {}

        existing_payslip_data = existing_content.get(
            "payslips", {"data": []})

        title_date = datetime(
            month=payslip_data["month"], year=payslip_data["year"], day=1)
        current_title = title_date.strftime("%b %Y").upper()
        update_index = -1
        for i, existing_payslip in enumerate(existing_payslip_data["data"]):
            title = existing_payslip["children"][1]["children"][0]["title"]
            if (title == current_title):
                update_index = i
                break

        cms_payslip = {
            "children": [
                {
                    "type": "image",
                    "url": "https://d22ss3ef1t9wna.cloudfront.net/dev/cms/2023-07-06/circleIcons/payslip.png",
                },
                {
                    "children": [{"title": current_title, "type": "title"}],
                    "styling": {"paddingLeft": "5%"},
                    "type": "container",
                },
                {
                    "type": "button",
                    "title": "Open PDF",
                    "variant": "filled",
                    "url": f"https://d22ss3ef1t9wna.cloudfront.net/prod/pdf_viewer/viewer.html?file={asset_url}",
                    "styling": {
                        "marginVertical": 0,
                        "width": 100,
                        "marginRight": 50,
                        "padding": 0,
                    },
                },
            ],
            "navigate": {"type": "cms", "params": {"blogKey": "payslips"}},
            "secondColumnStyle": {"flex": 1, "paddingLeft": 15},
            "type": "threeColumn",
            "widths": ["10%", "80%", "10%"],
        }

        if (update_index > -1):
            existing_payslip_data["data"][update_index] = cms_payslip
        else:
            existing_payslip_data["data"].append(cms_payslip)
        return existing_payslip_data

    def run(self, payload):
        # check typecasting
        payslips = payload["payslips"]

        payslips_data = Payslips.aggregate(
            get_payslip_aggregation_info(payslips))

        for payslip_data in payslips_data:
            """Generate Payslips"""
            payslip_gen_service = PayslipGenerationService(payslip_data)
            payslip_fd = payslip_gen_service.generate_payslip()

            # employer_id/year-month

            """Upload Payslips"""
            payslip_upload_service = PayslipUploadService(
                employment_id=payslip_data["employment_details"]["employment_id"], employer_id=payslip_data["employer_id"], year=payslip_data["year"], month=payslip_data["month"])
            asset_url = payslip_upload_service.upload_document(
                fd=payslip_fd, payslip_data=payslip_data)

            """Update CMS"""
            existing_payslip_data = self.cms_payslip_builder(
                payslip_data, asset_url)
            CMS.set_content(
                group=payslip_data["unipeEmployeeId"], content_type="payslips", content=existing_payslip_data)
