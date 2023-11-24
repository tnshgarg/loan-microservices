from admin.components.fields import CustomUrlField
from admin.views.admin_view import AdminView
from dal.models.employer import Employer
from dal.models.sales_users import SalesUser
from services.employer.uploads.employer_upload_service import EmployerUploadService
from starlette_admin import CollectionField, StringField, URLField
from typing import Any, Dict, List, Optional, Union
from starlette.requests import Request
from admin.utils import DictToObj
from starlette_admin.exceptions import ActionFailed
from starlette_admin.actions import row_action
from starlette_admin._types import RowActionsDisplayType
from starlette.requests import Request
from starlette.datastructures import FormData
from typing import Any


class EmployerApprovalView(AdminView):

    identity = "employer_approval"
    name = "Employer Approval"
    label = "Employer Approval"
    icon = "fa fa-users"
    model = Employer
    pk_attr = "_id"
    fields = [
        StringField("_id"),
        StringField("companyName"),
        StringField("companyType"),
        StringField("employeeCount"),
        # JSONField("registrar"),
        StringField("updatedAt"),
        StringField("approvalStage"),
        CollectionField("documents", fields=[
            CollectionField("drive", fields=[
                URLField("pan"),
                URLField("agreement"),
                URLField("gst"),
            ])
        ])
    ]

    row_actions = ["view", "edit", "upload_details",
                   "approve_employer"]
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

        user = request.state.user
        data: FormData = await request.form()
        employer_notes = data.get("employer-notes")
        employer_agreement = data.get("employer-agreement")
        employer_pan = data.get("employer-pan")
        employer_gst = data.get("employer-gst")
        print("DATA: ", data)

        employer_upload_service = EmployerUploadService(employer_id=pk)
        # Assuming upload_documents expects a list of dictionaries for each document
        employer_upload_service.upload_document(
            "pan", employer_pan.file, employer_pan.content_type)
        employer_upload_service.upload_document(
            "agreement", employer_agreement.file, employer_agreement.content_type)
        employer_upload_service.upload_document(
            "gst", employer_gst.file, employer_gst.content_type)
        employer_upload_service.update_employer({
            "sales_user_id": user,
            "documents.notes": employer_notes
        })
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

        print(employer_notes, doc_employer_agreement,
              doc_employer_gst, doc_employer_pan)

        return "The article was successfully marked as published"

    async def find_all(self, request: Request, skip: int = 0, limit: int = 100,
                       where: Union[Dict[str, Any], str, None] = None,
                       order_by: Optional[List[str]] = None) -> List[Any]:
        if where is None:
            where = {"_id": None}
        # Retrieve userType, if he is SM, RM, or Manager from request.session
        username = request.session.get("username", None)
        if username:
            user_data = SalesUser.find_one({"email": username})
            if user_data:
                user_type = user_data.get("type")
                sales_user_id = user_data.get("_id")
                print("User Type:", user_type)

        if user_type == "admin":
            where = {}
        elif sales_user_id and (user_type == "sm" or user_type == "rm"):
            where = {"salesUsers": {"$elemMatch": {"salesId": sales_user_id}}}

        res = Employer.find(where)
        res.skip(skip).limit(limit)
        # TODO: add order by to the cursor
        find_all_res = []
        for employer_lead in res:
            find_all_res.append(DictToObj(employer_lead))
        return find_all_res
