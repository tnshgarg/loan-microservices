import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dal.models.db_manager import DBManager
from kyc_service.config import Config
from kyc_service.main import app as kyc_app
from ops.main import employer_app
from admin.main import admin_app
app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://qa.d2ofz3ql5xiuyy.amplifyapp.com",
    "https://dev.d2ofz3ql5xiuyy.amplifyapp.com",
    "https://sales-webapp.unipe.money"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_db_client():
    stage = os.environ["STAGE"]
    DBManager.init(stage=stage, asset="ops-service")


@app.on_event("shutdown")
def shutdown_db_client():
    DBManager.terminate()


@app.get("/ping")
async def ping():
    return {"status": 200, "stage": Config.STAGE}

app.mount(f"/{Config.STAGE}/ops-admin", admin_app)
app.mount(f"/{Config.STAGE}/ops-service", employer_app)
app.mount("/", kyc_app)


print(app)
