import sys
import os
import bson

current_dir = os.path.dirname(os.path.abspath(__file__))
grandparent_dir = os.path.dirname(os.path.dirname(current_dir))

sys.path.append(grandparent_dir)

from starlette_admin.contrib.mongoengine import ModelView
from starlette_admin.exceptions import ActionFailed
from starlette_admin.actions import row_action
from starlette_admin._types import RowActionsDisplayType
from starlette.requests import Request
from starlette.datastructures import FormData
from typing import Any
from kyc_service.services.storage.uploads.media_upload_service import MediaUploadService
from kyc_service.services.storage.uploads.drive_upload_service import DriveUploadService

class EmployerUploadService(MediaUploadService):

    def __init__(self,
                 sales_user_id: bson.ObjectId,
                 gdrive_upload_service: DriveUploadService,
                 ) -> None:
        super().__init__(None, sales_user_id, gdrive_upload_service, None, None)
        self.sales_user_id= sales_user_id
        self.gdrive_upload_service= gdrive_upload_service


    def upload_agreement(self, agreement):
        upload_agreement_drive_url = self._upload_media(
            form_file=agreement,
            filename="agreement"
        )
        return upload_agreement_drive_url
    

    def upload_pan(self, pan):
        upload_pan_drive_url = self._upload_media(
            form_file=pan,
            filename="pan"
        )
        return upload_pan_drive_url
    

    def upload_gst(self, gst):
        upload_gst_drive_url = self._upload_media(
            form_file=gst,
            filename="gst"
        )
        return upload_gst_drive_url

class EmployerApprovalView(ModelView):


    # def __init__(self,
    #              sales_user_id: bson.ObjectId,
    #              gdrive_upload_service: DriveUploadService,
    #              ) -> None:
    #     super().__init__(
    #         sales_user_id,
    #         gdrive_upload_service,
    #     )
    # @classmethod
    # def get_row_actions(cls, request):
    #     user_roles = request.state.user['roles']

    #     actions_for_roles = {
    #         'admin': ["view", "edit", "upload_details", "approve_employer", "delete"],
    #         'rm': ["view", "edit", "upload_details"],
    #         'sm': ["view"],
    #     }

    #     actions = []
    #     for role in user_roles:
    #         actions.extend(actions_for_roles.get(role, []))

    #     return list(set(actions))

    # row_actions = get_row_actions()
    row_actions = ["view", "edit", "upload_details",
                   "approve_employer", "delete"]
    # fields = ["externalCustomerId","externalInstrementId"]
    row_actions_display_type = RowActionsDisplayType.ICON_LIST

    @row_action(
        name="upload_details",
        text="Upload Details",
        confirmation="Upload Employer Approval Documents",
        icon_class="fas fa-upload",
        submit_btn_text="Yes, proceed",
        submit_btn_class="btn-success",
        action_btn_class="btn-info",
        form="""
        <form>
            <div class="mt-3">
                <input type="text" class="form-control mt-2" name="employer-notes" placeholder="Enter Notes">
                <div class="mt-3">
                <label>Upload Agreement</label>
                <input type="file" class="form-control mt-2" name="employer-agreement" placeholder="Upload Agreement">
                </div>
                <div class="mt-3">
                    <label>Upload PAN</label>
                    <input
                        type="file"
                        class="form-control mt-2"
                        name="employer-pan"
                        placeholder="Upload PAN"
                    />
                    </div>
                    <div class="mt-3">
                    <label>Upload GST</label>
                    <input
                        type="file"
                        class="form-control mt-2"
                        name="employer-gst"
                        placeholder="Upload GST"
                    />
                    </div>

            </div>
        </form>
        """,
    )
    async def upload_details_row_action(self, request: Request, pk: Any) -> str:
        # Write your logic here

        user = request.state.user
        data: FormData = await request.form()
        employer_notes = data.get("employer-notes")
        doc_employer_agreement = data.get("employer-agreement")
        # doc_employer_pan = data.get("employer-pan")
        # doc_employer_gst = data.get("employer-gst")
        print("DATA: ", data)
        employer_upload_service =  EmployerUploadService(user, gdrive_upload_service=DriveUploadService)
        # pan_url = self._upload_media(doc_employer_pan, f"{doc_employer_pan.filename}-{user}")
        # pan_url = employer_upload_service.upload_pan(self, doc_employer_pan)
        agreement_url = employer_upload_service.upload_agreement(self, doc_employer_agreement)
        # gst_url = employer_upload_service.upload_gst(self, doc_employer_gst)
        print("pan_url: ", pan_url)

        if False:
            # Display meaningfully error
            raise ActionFailed("Sorry, We can't proceed this action now.")
        # Display successfully message
        return "You have successfully uploaded details of Employer"

    @row_action(
        name="approve_employer",
        text="Approve Employer",
        confirmation="Approve or Reject Employer Approval Request",
        icon_class="fas fa-check",
        submit_btn_text="Yes, proceed",
        submit_btn_class="btn-success",
        action_btn_class="btn-info",
        form="""
        <form>
            <div class="form-check mt-3">
                <input class="form-check-input" type="radio" name="approval-status" id="approve" value="approve" checked>
                <label class="form-check-label" for="approve">
                    Approve
                </label>
            </div>
            <div class="form-check mt-3">
                <input class="form-check-input" type="radio" name="approval-status" id="deny" value="deny">
                <label class="form-check-label" for="deny">
                    Deny
                </label>
            </div>
        </form>
        """,
    )
    async def approve_employer_row_action(self, request: Request, pk: Any) -> str:
        # Write your logic here

        data: FormData = await request.form()
        employer_notes = data.get("employer-notes")
        doc_employer_agreement = data.get("employer-agreement")
        doc_employer_pan = data.get("employer-pan")
        doc_employer_gst = data.get("employer-gst")

        if False:
            # Display meaningfully error
            raise ActionFailed("Sorry, We can't proceed this action now.")
        # Display successfully message
        return "The article was successfully marked as published"
