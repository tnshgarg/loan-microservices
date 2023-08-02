from typing import Any
from uuid import UUID
import bson
from pydantic import BaseModel, Field


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    unipe_employee_id: Any = None
    exp: int = None
    sales_user_id: Any = None
    client_id: str = None
