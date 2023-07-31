import os

import uvicorn
from fastapi import FastAPI

from dal.models.db_manager import DBManager
from ops.router import router

employer_approval_app = FastAPI()


@employer_approval_app.on_event("startup")
def startup_db_client():
    stage = os.environ["stage"]
    DBManager.init(stage=stage)


@employer_approval_app.on_event("shutdown")
def shutdown_db_client():
    DBManager.terminate()


employer_approval_app.include_router(router)


if __name__ == "__main__":
    fastapi_host = os.environ["fastapi_host"]
    uvicorn.run("main:employer_approval_app", host=fastapi_host,
                port=5000, log_level="info", reload=True)
