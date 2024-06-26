from bson import ObjectId
from pydantic import BaseModel, Field


class ApolloLoanPayload(BaseModel):
    employer_id: str = Field(alias="employerId")
    unipe_employee_id: str = Field(alias="unipeEmployeeId",)
    loan_application_id: str = Field(alias="loanApplicationId")
    offer_id: str = Field(alias="offerId")
    loan_type: str = Field(alias="loanType")
