from admin.views.admin_view import AdminView
from dal.models.employer import Employer
from dal.models.sales_users import SalesUser
from services.employer.uploads.employer_upload_service import EmployerUploadService
from starlette_admin import CollectionField, StringField, URLField
from typing import Any, Dict, List, Optional, Union
from starlette.requests import Request
from admin.utils import DictToObj, MultiFormDataParser
from starlette_admin.actions import row_action
from starlette_admin._types import RowActionsDisplayType
from starlette.requests import Request
from starlette.datastructures import FormData
from typing import Any

TEMPLATE_PATHS = {
    "document_upload": "admin/templates/employer_approval/document_upload.html",
    "approve_or_deny": "admin/templates/employer_approval/approve_or_deny.html",
}


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
        StringField("updatedAt"),
        StringField("approvalStage"),
        CollectionField("documents", fields=[
            CollectionField("drive", fields=[
                URLField("pan"),
                URLField("agreement"),
                URLField("gst"),
            ]),
            StringField("notes")
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
        form=open(TEMPLATE_PATHS.get("document_upload"),
                  'r', encoding='utf-8').read()
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

        documents = {
            "pan": employer_pan,
            "agreement": employer_agreement,
            "gst": employer_gst
        }
        sucessfully_uploaded_docs = []
        for doc_type, doc in documents.items():
            if doc and doc.size > 0:
                employer_upload_service.upload_document(
                    doc_type, doc.file, doc.content_type)
                sucessfully_uploaded_docs.append(doc_type)

        employer_upload_service.update_employer({
            "sales_user_id": user,
            "documents.notes": employer_notes
        })
        return f"You have successfully uploaded the {[doc for doc in sucessfully_uploaded_docs]} of Employer"

    @row_action(
        name="approve_employer",
        text="Approve Employer",
        confirmation="Approve or Reject Employer Approval Request",
        icon_class="fas fa-check",
        submit_btn_text="Yes, proceed",
        submit_btn_class="btn-success",
        action_btn_class="btn-info",
        form=open(TEMPLATE_PATHS.get("approve_or_deny"),
                  'r', encoding='utf-8').read()
    )
    async def approve_employer_row_action(self, request: Request, pk: Any) -> str:
        data = await request.form()
        approval_status = MultiFormDataParser.parse(data, "approval_status")
        employer_upload_service = EmployerUploadService(employer_id=pk)
        employer_approval_status = "approved" if approval_status == "approve" else "denied"

        employer_upload_service.update_employer({
            "approvalStage": employer_approval_status
        })

        return f"The Employer is successfully {employer_approval_status}"

    async def find_all(self, request: Request, skip: int = 0, limit: int = 100,
                       where: Union[Dict[str, Any], str, None] = None,
                       order_by: Optional[List[str]] = None) -> List[Any]:

        if where is None:
            where = {"_id": None}

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
        order_by
        find_all_res = []
        for employer_lead in res:
            find_all_res.append(DictToObj(employer_lead))
        return find_all_res
