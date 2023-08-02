
from typing import Annotated

from fastapi import HTTPException, Header, status
from kyc_service.auth import decode_token
from kyc_service.schemas.auth import TokenPayload


async def get_current_session(authorization: Annotated[str | None, Header()] = None) -> TokenPayload:
    try:
        payload = decode_token(authorization)
        return TokenPayload.model_construct(**payload)
    except Exception as e:
        message = str(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={"WWW-Authenticate": ""},
        )
