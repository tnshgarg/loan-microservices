
from typing import Annotated

from fastapi import HTTPException, Header, status
from kyc.auth import decode_token
from kyc.schemas.auth import TokenPayload, SalesTokenPayload


async def get_sales_current_session(authorization: Annotated[str | None, Header()] = None) -> SalesTokenPayload:
    try:
        payload = decode_token(authorization)
        return SalesTokenPayload.construct(**payload)
    except Exception as e:
        message = str(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={"WWW-Authenticate": ""},
        )


async def get_current_session(authorization: Annotated[str | None, Header()] = None) -> TokenPayload:
    try:
        payload = decode_token(authorization)
        return TokenPayload.construct(**payload)
    except Exception as e:
        message = str(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={"WWW-Authenticate": ""},
        )
