import mongoengine as me

class ScheduledJobModel(me.Document):
    _id = me.ObjectIdField("_id", label="Employee Id")
    created_at = me.ObjectIdField("created_at")
    provider = me.StringField("provider")
    account_id = me.StringField("account_id")
    account_name = me.StringField("account_name")
    payment_id = me.StringField("payment_id")
    status = me.StringField("status")
    amount = me.StringField("amount")
    description = me.StringField("description")
    email = me.StringField("email")
    contact = me.StringField("contact")
    message = me.StringField("message")

