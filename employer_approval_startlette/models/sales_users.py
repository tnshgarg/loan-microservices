from mongoengine import StringField, ObjectIdField, Document


class SalesUsers(Document):
    meta = {'collection': 'sales_users'}
    _id = ObjectIdField()
    email = StringField(required=True)
    type = StringField()
    name = StringField()
    hashed_pw = StringField()
    asset = StringField()
    updatedAt = StringField()
    phone = StringField()
