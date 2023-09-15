from pydantic import BaseModel, Field

# add date field as well , get from async-jobs


class RequestDate(BaseModel):

    # required fields
    year: int
    month: int
    day: int


class EmployerEmailPayload(BaseModel):

    # required fields
    employer_id: str = Field(alias="employerId")
    request_date: RequestDate = Field(alias="requestDate")
