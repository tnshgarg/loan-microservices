from admin.views.admin_view import AdminView
from dal.models.loan_applications import LoanApplications
from starlette_admin import StringField, BooleanField, DateTimeField, CollectionField
from admin.models.loanApplication import LoanApplication

class LoanApplicationsView(AdminView):
    document = LoanApplication
    identity = "loan_application"
    name = "Loan Application"
    label = "Loan Applications"
    icon = "fa fa-clipboard"
    model = LoanApplications
    pk_attr = "_id"
    fields = [
        StringField("_id"),
        StringField("unipeEmployeeId"),
        StringField("asset"),
        StringField("creditLimit"),
        StringField("creditUtilization"),
        CollectionField("data", [
            StringField("locStatus"),
            StringField("nextDisbursementLoanId"),
        ]),
        StringField("ongoingOfferId"),
        DateTimeField("expiry"),
        StringField("externalLoanId"),
        StringField("month"),
        StringField("provider"),
        DateTimeField("updatedAt"),
        StringField("year"),
        CollectionField("lastApplicationStatus", fields=[
            StringField("eventType"),
            StringField("eventStatus")
        ])
    ]
