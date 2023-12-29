import bson
from starlette.requests import Request
from admin.views.admin_view import AdminView
from dal.models.employees import Employee
from starlette_admin import BooleanField, StringField


class EmployeesView(AdminView):
    identity = "employees"
    name = "Employees"
    label = "Employees"
    icon = "fa fa-users"
    model = Employee
    pk_attr = "_id"
    fields = [
        StringField("_id", label="Employee Id"),
        StringField("employeeName"),
        StringField("mobile"),
        StringField("companyName"),
        StringField("email"),
        StringField("gender"),
        StringField("nationality"),
        StringField("dob"),
        StringField("altMobile"),
        StringField("motherName"),
        StringField("qualification"),
        StringField("currentAddress"),
        BooleanField("profileComplete"),
        StringField("remark"),
    ]

    def is_accessible(self, request) -> bool:
        roles = request.state.user["roles"]
        return "employees" in roles

    def can_edit(self, request: Request) -> bool:
        return "admin" in request.state.user["roles"]
