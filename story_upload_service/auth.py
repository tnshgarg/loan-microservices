from typing import Any
from pydantic import BaseModel


class UserUploadSchema(BaseModel):
    status: int
    video: str
