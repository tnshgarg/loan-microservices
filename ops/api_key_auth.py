import os

from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

# Get environment variables
OPS_MICROSERVICE_API_KEY = os.environ["OPS_MICROSERVICE_API_KEY"]

api_key_header = APIKeyHeader(
    name="ops-microservice-api-key", auto_error=False)


async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == OPS_MICROSERVICE_API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )
