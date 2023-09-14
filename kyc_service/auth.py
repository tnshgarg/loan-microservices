from datetime import datetime, timedelta
from typing import Any, Union
import bson
from jose import jwt

from kyc_service.config import Config


def create_access_token(unipe_employee_id: str, client_id: str, sales_user_id: str = None) -> str:
    expires_delta = datetime.utcnow() + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    if sales_user_id is None:
        to_encode = {
            "exp": expires_delta,
            "sub": unipe_employee_id,
            "client_id": client_id,
            "type": "employee"
        }
    else:
        to_encode = {
            "exp": expires_delta,
            "sub": unipe_employee_id,
            "sales_user_id": sales_user_id,
            "client_id": client_id,
            "type": "sales"
        }
    encoded_jwt = jwt.encode(
        to_encode, Config.JWT_SECRET_KEY, Config.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(unipe_employee_id: str, client_id: str, sales_user_id: str = None) -> str:
    expires_delta = datetime.utcnow() + timedelta(minutes=Config.REFRESH_TOKEN_EXPIRE_MINUTES)
    if sales_user_id is None:
        to_encode = {
            "exp": expires_delta,
            "sub": unipe_employee_id,
            "client_id": client_id,
            "type": "employee"
        }
    else:
        to_encode = {
            "exp": expires_delta,
            "sub": unipe_employee_id,
            "sales_user_id": sales_user_id,
            "client_id": client_id,
            "type": "sales"
        }
    encoded_jwt = jwt.encode(
        to_encode, Config.JWT_REFRESH_SECRET_KEY, Config.JWT_ALGORITHM)
    return encoded_jwt


def valid_client(client_id: str, client_secret: str) -> bool:
    return client_id in Config.OAUTH_CLIENTS and Config.OAUTH_CLIENTS[client_id] == client_secret


def decode_token(token: str):
    decoded_token = jwt.decode(
        token,
        key=Config.JWT_SECRET_KEY,
        algorithms=[Config.JWT_ALGORITHM]
    )
    if decoded_token["type"] == "employee":
        decoded_token["unipe_employee_id"] = bson.ObjectId(decoded_token["sub"])
    else:
        decoded_token["unipe_employee_id"] = bson.ObjectId(decoded_token["sub"])
        decoded_token["sales_user_id"] = bson.ObjectId(
            decoded_token["sales_user_id"])
    return decoded_token
