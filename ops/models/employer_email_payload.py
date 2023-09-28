from datetime import datetime

from pydantic import BaseModel, Field

# add date field as well , get from async-jobs


class RequestDate(BaseModel):

    # required fields
    year: int
    month: int
    day: int

    # return formatted date
    def get_date_string(self):
        date_string = f"{self.day}/{self.month}/{self.year}"
        return date_string


class EmployerRepaymentsEmailPayload(BaseModel):

    # required fields
    employer_id: str = Field(alias="employerId")
    request_date: RequestDate = Field(alias="requestDate")


class EmployerDisbursementsEmailPayload(BaseModel):

    # required fields
    employer_id: str = Field(alias="employerId")
    request_date: datetime = Field(alias="requestDate")
