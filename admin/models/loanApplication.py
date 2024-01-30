import mongoengine as me

class LoanApplication(me.Document):
    _id = me.ObjectIdField("_id", label="Employee Id")
    unipeEmployeeId = me.ObjectIdField("unipeEmployeeId")
    asset = me.StringField("asset")
    creditLimit = me.StringField("creditLimit")
    creditUtilization = me.StringField("creditUtilization")
    ongoingOfferId = me.StringField("ongoingOfferId")
    expiry = me.DateTimeField("expiry")
    externalLoanId = me.StringField("externalLoanId")
    month = me.StringField("month")
    provider = me.StringField("provider")
    updatedAt = me.DateTimeField("updatedAt")
    year = me.StringField("year")


