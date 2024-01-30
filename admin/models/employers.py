import enum
import mongoengine as me
from .employees import Employees
from admin.constants import BusinessType

class Registrar(me.EmbeddedDocument):
    name = me.StringField(min_length=3)
    email = me.StringField(min_length=3)
    mobile = me.StringField(min_length=3)
    designation = me.StringField(min_length=3)

class StarletteEmployers(me.Document):
    externalCustomerId = me.StringField(min_length=3)
    externalInstrementId = me.StringField(min_length=3)
    approvalStage = me.StringField(min_length=3)
    companyName = me.StringField(min_length=3)
    companyType = me.StringField(min_length=3)
    employeeCount = me.StringField(min_length=3)
    registrar = me.EmbeddedDocumentField(Registrar)

class Constitution(str, enum.Enum):
    Proprietorship = "Proprietorship"
    PrivateLimited = "Private Limited"
    Proprietor = "Proprietor"
    privateLimited = "private limited"
class ApprovalStage(str, enum.Enum):
    pending = "pending"
    inprogress = "inprogress"
    approved = "approved"
    denied = "denied"

class EmployerApprovals(me.Document):
        _id = me.StringField("_id", label="Employer ID")
        companyName = me.StringField("companyName", label="Name")
        companyType = me.StringField("companyType", label="Company Type")
        employeeCount = me.StringField("employeeCount", label="No. of Employees")
        updatedAt = me.DateTimeField("updatedAt", label="Last Updated At")
        approvalStage = me.EnumField(label="Approval Stage",enum=ApprovalStage)
        documents = me.ListField("documents", fields=[
            me.ListField("drive", fields=[
                me.URLField(
                    "pan",
                    exclude_from_edit=True,
                    exclude_from_list=True,
                    exclude_from_create=True,
                ),
                me.URLField(
                    "agreement",
                    exclude_from_edit=True,
                    exclude_from_list=True,
                    exclude_from_create=True,
                ),
                me.URLField(
                    "gst",
                    exclude_from_edit=True,
                    exclude_from_list=True,
                    exclude_from_create=True,
                ),
            ]),
            me.StringField("notes", label="Notes", exclude_from_create=True)
        ]),
        documentsUploaded = me.BooleanField(
            "documentsUploaded",
            label="Document Upload Status",
            exclude_from_edit=True,
            exclude_from_detail=True
        )

class CommercialLoans(me.Document):  
        _id = me.StringField("_id", label="Employer ID")
        employerId = me.ListField(me.ReferenceField(EmployerApprovals))
        companyName = me.StringField("companyName", label="Name")
        commercial_loan_details= me.ListField("commercial_loan_details", fields=[
            me.IntField("annual_turn_over", required=True),
            me.StringField("business_category", required=True),
            me.StringField("industry_type", required=True),
            me.EnumField(label="constitution", enum=Constitution),
        ]),
        employer_address=me.ListField("employer_address", fields=[
            me.StringField("address", required=True),
            me.StringField("city", required=True),
            me.StringField("state", required=True),
            me.StringField("pin", required=True),
        ]),
        disbursement_bank_account=me.ListField("disbursement_bank_account", fields=[
            me.StringField("account_number", required=True),
            me.StringField("ifsc", required=True),
        ]),
        employer_ids=me.ListField("employer_ids", fields=[
            me.StringField("pan_number", required=True),
            me.StringField("gst_number", required=True, label="GST Number"),
            me.StringField(
                "registration_number",
                placeholder="NA",
                label="Company Registration Number"
            ),
            me.StringField(
                "udyam_number",
                placeholder="NA"
            ),
            me.StringField(
                "duns_number",
                placeholder="999999999"
            ),
        ]),
        promoters = me.ListField("promoters", fields=[
                me.ListField(me.ReferenceField(Employees)),
                me.StringField("aadhaar", required=True),
                me.StringField("pan", required=True),
                me.StringField("currentAddress", required=True,
                            label="Current Address"),
                me.BooleanField("key_promoter", required=True,
                             label="Is Key Promoter ?")
            ], required=True),
        me.ListField("document_uploads", fields=[
            me.FileField(
                "gst_certificate",
                required=True,
                display_template="fields/file.html",
                exclude_from_list=True),
            me.FileField(
                "bank_statement",
                required=True,
                display_template="fields/file.html",
                exclude_from_list=True),
            me.FileField(
                "bureau",
                required=True,
                display_template="fields/file.html",
                exclude_from_list=True),
            me.FileField(
                "incorporation_certificate",
                required=True,
                display_template="fields/file.html",
                exclude_from_list=True)
        ], required=True),
        businessType = me.EnumField(label="businessType", enum=BusinessType),
