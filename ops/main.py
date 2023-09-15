import os

import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from dal.models.db_manager import DBManager
from ops.auth import auth_router
from ops.routers.employer_approval_router import employer_approval_router
from ops.routers.employer_emails_router import employer_emails_router

# Get environment variables
FASTAPI_HOST = os.environ["fastapi_host"]
SECRET_KEY = os.environ["SECRET_KEY"]

# App Initialization
employer_app = FastAPI()
employer_app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


@employer_app.on_event("startup")
def startup_db_client():
    stage = os.environ["STAGE"]
    DBManager.init(stage=stage, asset="ops-service")


@employer_app.on_event("shutdown")
def shutdown_db_client():
    DBManager.terminate()


@employer_app.get("/ping")
def ping():
    return {
        "status": "success",
        "message": "pong",
    }


employer_app.include_router(auth_router)
employer_app.include_router(employer_approval_router)
employer_app.include_router(employer_emails_router)


if __name__ == "__main__":
    uvicorn.run("main:employer_app", host=FASTAPI_HOST,
                port=5000, log_level="info", reload=True)
