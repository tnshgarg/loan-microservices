from pydantic import BaseModel, Field


class CognitoSignUp(BaseModel):

    # required fields
    employer_id: str = Field(alias="sub")
    company_name: str = Field(alias="custom:company_name")
    sales_id: str = Field(alias="custom:sales_id")

    # other company details
    email: str = Field(default=None)
    email_verified: str = Field(default=None)
    phone_number: str = Field(default=None)
    phone_number_verified: str = Field(default=None)
    company_type: str = Field(alias="custom:company_type", default=None)
    employee_count: str = Field(alias="custom:employee_count", default=None)
    employee_name: str = Field(alias="name", default=None)
    employee_designation: str = Field(alias="custom:designation", default=None)
    cognito_user_status: str = Field(alias="cognito:user_status", default=None)
    created_at: str = Field(alias="createdAt", default=None)
