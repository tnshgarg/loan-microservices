from typing import Any
from uuid import UUID
import bson
from pydantic import BaseModel, Field


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class SalesTokenPayload(BaseModel):
    unipe_employee_id: Any = None
    exp: int = None
    sales_user_id: Any = None
    client_id: str = None
    type: str = None


class TokenPayload(BaseModel):
    unipe_employee_id: Any = None
    exp: int = None
    client_id: str = None
    type: str = None
class GenerateOtpPayload(BaseModel):
    mobile_number: str
    provider: str
    offer_id: str

class VerifyOtpPayload(BaseModel):
    mobile_number: str = None
    otp : str = None
    provider: str = None,
    offer_id: str = None