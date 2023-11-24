from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from dal.models.db_manager import DBManager
from dal.models.employees import Employee
from dal.models.sales_users import SalesUser
from kyc.auth import create_access_token, create_refresh_token, valid_client
from fastapi.middleware.cors import CORSMiddleware

from kyc.schemas.auth import TokenSchema

token_router = APIRouter()


@token_router.post('/token', summary="Create access and refresh tokens for sales_users", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not valid_client(form_data.client_id, form_data.client_secret):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Client"
        )
    employee = Employee.find_one({"mobile": form_data.username})
    if employee["asset"] == "sales":
        sales_user = SalesUser.find_one({"hashed_pw": form_data.password})
        if employee is None or sales_user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can't Locate User"
            )
        return {
            "access_token": create_access_token(
                unipe_employee_id=str(employee["_id"]),
                sales_user_id=str(sales_user["_id"]),
                client_id=form_data.client_id
            ),
            "refresh_token": create_refresh_token(
                unipe_employee_id=str(employee["_id"]),
                sales_user_id=str(sales_user["_id"]),
                client_id=form_data.client_id
            ),
        }
    else:
        if employee is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can't Locate User"
            )
        return {
            "access_token": create_access_token(
                unipe_employee_id=str(employee["_id"]),
                client_id=form_data.client_id
            ),
            "refresh_token": create_refresh_token(
                unipe_employee_id=str(employee["_id"]),
                client_id=form_data.client_id
            ),
        }
