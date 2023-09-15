from pydantic import BaseModel, Field

# add date field as well , get from async-jobs


class EmployerEmailPayload(BaseModel):

    # required fields
    employer_id: str = Field(alias="employerId")
