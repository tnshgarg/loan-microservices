import mongoengine as me
import enum
from admin.models.employers import EmployerApprovals
from admin.models.employees import Employees

class LoanType(enum.Enum):
    COMMERCIAL = "COMMERCIAL"
    PERSONAL = "PERSONAL"


class LoanProvider(enum.Enum):
    apollo = "apollo"
    liquiloans = "liquiloans"


class Offer(me.Document):
    _id = me.ObjectIdField("_id", label="Offer Id")
    employerId = me.ListField(me.ReferenceField(EmployerApprovals))
    unipeEmployeeId = me.ListField(me.ReferenceField(Employees))
    provider = me.EnumField(label="provider", enum=LoanProvider)
    loanType = me.EnumField(label="loanType", enum=LoanType)
    year = me.StringField("year")
    month = me.StringField("month")
    loanAmount = me.IntField("loanAmount")
    limitAmount = me.IntField("limitAmount")
    eligibleAmount = me.IntField("eligibleAmount")
    dueDate = me.DateField("dueDate")
    live = me.BooleanField("live")
    availed = me.BooleanField("availed")
    availedAt = me.DateField("availedAt")
    disbursed = me.BooleanField("disbursed")
    employmentId = me.StringField("employmentId")
    fees = me.DecimalField("fees")
    paid = me.BooleanField("paid")
    stage = me.StringField("stage")
    updatedAt = me.DateTimeField("updatedAt")
    disbursedAt = me.DateTimeField("disbursedAt")
    disbursementId = me.StringField("disbursementId")
    repaymentId = me.StringField("repaymentId")
    paidAmount = me.StringField("paidAmount")
    
    

