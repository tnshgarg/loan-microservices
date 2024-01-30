import mongoengine as me

class Employees(me.Document):
    _id = me.ObjectIdField("_id", label="Employee Id")
    employeeName = me.StringField("employeeName")
    mobile = me.StringField("mobile")
    companyName = me.StringField("companyName")
    email = me.StringField("email")
    gender = me.StringField("gender")
    nationality = me.StringField("nationality")
    dob = me.StringField("dob")
    altMobile = me.StringField("altMobile")
    motherName = me.StringField("motherName")
    qualification = me.StringField("qualification")
    currentAddress = me.StringField("currentAddress")
    profileComplete = me.BooleanField("profileComplete")
    remark = me.StringField("remark")
