from pydantic import BaseModel, Field


class EmployerInfo(BaseModel):

    # required fields
    employer_id: str = Field(alias="employerId")
