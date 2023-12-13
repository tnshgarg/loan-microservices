import enum
from typing import Any, Dict, List, Optional, Union

import bson
from admin.views.admin_view import AdminView
from dal.models.employer import Employer
from dal.models.sales_users import SalesUser
from services.employer.uploads.employer_upload_service import EmployerUploadService
from starlette_admin import CollectionField, EnumField, StringField, URLField, BooleanField, DateTimeField
from starlette.requests import Request
from admin.utils import DictToObj, MultiFormDataParser
from starlette_admin.actions import row_action
from starlette_admin._types import RowActionsDisplayType
from starlette_admin.exceptions import ActionFailed
from starlette.datastructures import FormData

TEMPLATE_PATHS = {
    "document_upload": "admin/templates/employer_approval/document_upload.html",
    "approve_or_deny": "admin/templates/employer_approval/approve_or_deny.html",
}

REQUIRED_DOCUMENTS = ["gst", "pan", "agreement"]


class ApprovalStage(str, enum.Enum):
    PENDING = "pending"
    INPROGRESS = "inprogress"
    APPROVED = "approved"
    DENIED = "denied"


def create_user_filter(user_type: str, sales_user_id: bson.ObjectId):
    if user_type not in ["admin", "sm", "rm"]:
        user_type = "rm"
    if user_type == "admin":
        where = {}
    elif sales_user_id and (user_type == "sm" or user_type == "rm"):
        where = {"salesUsers": {"$elemMatch": {"salesId": sales_user_id}}}
    return where


def get_sales_user_data(request: Request):
    if request.state.user is not None:
        return [request.state.user["roles"], request.state.user["sales_id"]]
    raise ActionFailed("User Not Present in the Database")


class EmployerApprovalView(AdminView):
    identity = "employer"
    name = "Employers"
    label = "Employers"
    icon = "fa fa-user-check"
    model = Employer
    pk_attr = "_id"
    fields = [
        StringField("_id", label="Employer ID"),
        StringField("companyName", label="Name"),
        StringField("companyType", label="Company Type"),
        StringField("employeeCount", label="No. of Employees"),
        DateTimeField("updatedAt", label="Last Updated At"),
        EnumField("approvalStage", label="Approval Stage", enum=ApprovalStage),
        CollectionField("documents", fields=[
            CollectionField("drive", fields=[
                URLField("pan", exclude_from_edit=True,
                         exclude_from_list=True),
                URLField("agreement", exclude_from_edit=True,
                         exclude_from_list=True),
                URLField("gst", exclude_from_edit=True,
                         exclude_from_list=True),
            ]),
            StringField("notes", label="Notes", exclude_from_list=True)
        ], required=True),
        BooleanField(
            "documentsUploaded",
            label="Document Upload Status",
            exclude_from_edit=True,
            exclude_from_detail=True
        )
    ]
    row_actions_display_type = RowActionsDisplayType.ICON_LIST

    def is_accessible(self, request: Request) -> bool:
        return True

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

    def derive_filter(self, request, where):
        filter_ = {}
        if isinstance(where, str):
            filter_ = self.create_text_search_filter(where)

        [user_type, sales_user_id] = get_sales_user_data(request)

        user_filter = create_user_filter(user_type, sales_user_id)
        filter_.update(user_filter)
        return filter_

    async def find_all(self, request: Request, skip: int = 0, limit: int = 100,
                       where: Union[Dict[str, Any], str, None] = None,
                       order_by: Optional[List[str]] = None) -> List[Any]:
        filter_ = self.parse_where_clause(where)

        res = Employer.find(filter_)
        res.skip(skip).limit(limit)
        order_by
        find_all_res = []
        for employer_lead in res:
            uploaded_documents = employer_lead.get(
                "documents", {}).get("drive", {})
            employer_lead["documentsUploaded"] = True
            for document in REQUIRED_DOCUMENTS:
                if document not in uploaded_documents:
                    employer_lead["documentsUploaded"] = False
                    break

            find_all_res.append(DictToObj(employer_lead))
        return find_all_res

    async def count(self, request: Request, where: Union[Dict[str, Any], str, None] = None) -> int:
        filter_ = self.derive_filter(request, where)
        res = self.model.find(filter_)
        return len(list(res))
