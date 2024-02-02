import mongoengine as me

class Credential(me.Document):
    _id = me.ObjectIdField("_id", label="Employee Id")
    pId = me.StringField("pId", label="Employer Id")
    username = me.StringField("username", label="Username")
    password = me.StringField("password", label="Password")
    publicKey = me.StringField("publicKey", label="Public Key")
    portal = me.StringField("portal")
