from typing import Any

from starlette.datastructures import FormData
from starlette.requests import Request

from starlette_admin._types import RowActionsDisplayType
from starlette_admin.actions import link_row_action, row_action
from starlette_admin.exceptions import ActionFailed
from starlette_admin.contrib.mongoengine import ModelView


class EmployerApprovalView(ModelView):

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
                <input type="file" class="form-control mt-2" name="employer-pan" placeholder="Upload PAN">
                </div>
                <div class="mt-3">
                <label>Upload GST</label>
                <input type="file" class="form-control mt-2" name="employer-gst" placeholder="Upload GST">
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
        doc_employer_pan = data.get("employer-pan")
        doc_employer_gst = data.get("employer-gst")

        if False:
            # Display meaningfully error
            raise ActionFailed("Sorry, We can't proceed this action now.")
        # Display successfully message
        return "The article was successfully marked as published"

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
