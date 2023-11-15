from datetime import datetime
from enum import Enum
from starlette.requests import Request
import mongoengine as me


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
