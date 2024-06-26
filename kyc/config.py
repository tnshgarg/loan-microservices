
import json
import os


class OAuthConfig:
    GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
    GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]


class Config:
    STAGE = os.environ.get("STAGE", "dev")
    BUCKET = os.environ.get("S3_UPLOAD_BUCKET", "dev-unipe-campaign-assets")
    GOOGLE_CREDENTIALS = os.environ.get("GOOGLE_SERVICE_ACCOUNT_INFO")
    GRIDLINES = os.environ.get("GRIDLINES")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")
    REFRESH_TOKEN_EXPIRE_MINUTES = os.getenv(
        "REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7)
    OAUTH_CLIENTS = json.loads(os.getenv("OAUTH_CLIENTS", "{}"))
    KYC_STATUS_GOOGLE_SHEETS_ID = os.getenv("KYC_STATUS_GOOGLE_SHEETS_ID")
    GDRIVE_BASE_FOLDER_ID = os.getenv("GDRIVE_BASE_FOLDER_ID")
    ASSET = os.getenv("asset")
    SALES_APP_ASSET = "sales"
    MOBILE_APP_ASSET = "mobile-iota"
    WEBAPP_APP_ASSET = "web"
    SALES_APP_MAX_LIMIT = 10000

    KARZA = json.loads(os.getenv("KARZA_CREDENTIALS", "{}"))
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")

    APOLLO_CREDENTIALS = json.loads(os.getenv("APOLLO_CREDENTIALS", "{}"))
    APOLLO_LOAN_APPLICATION_HOOK = os.getenv("APOLLO_LOAN_APPLICATION_HOOK")

    GDRIVE_LOANS_BASE_FOLDERID = os.getenv('GDRIVE_LOANS_BASE_FOLDERID')
    LOANS_BUCKET = os.getenv('LOANS_BUCKET')
    LOANS_GOOGLE_SHEET = os.getenv('LOANS_GOOGLE_SHEET')
    LOANS_GDRIVE_BASE_FOLDER_ID = os.getenv("GDRIVE_LOANS_BASE_FOLDERID")

    GDRIVE_ADMIN_BASE_FOLDERID = os.getenv('GDRIVE_ADMIN_BASE_FOLDERID')
    ADMIN_BUCKET = os.getenv('ADMIN_BUCKET')
    ADMIN_GOOGLE_SHEET = os.getenv('ADMIN_GOOGLE_SHEET')

    GDRIVE_PAYSLIP_BASE_FOLDERID = os.getenv('GDRIVE_PAYSLIP_BASE_FOLDERID')
    PAYSLIP_BUCKET = os.getenv('PAYSLIP_BUCKET')
    PAYSLIP_GOOGLE_SHEET = os.getenv('PAYSLIP_GOOGLE_SHEET')

    IOTA_ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv(
        "IOTA_ACCESS_TOKEN_EXPIRE_MINUTES",
        10080
    )
    RZP_ACCOUNT_IDS = json.loads(os.getenv("RZP_ACCOUNT_IDS", "{}"))
    DECENTRO_CONFIG = json.loads(os.environ["decentro_config"])


class SlackWebhooks:
    DEV_CHANNEL = os.environ.get("SLACK_DEV_CHANNEL")
    GITHUB_ACTIONS = os.environ.get("SLACK_GITHUB_ACTIONS")
    METABASE_REPORTING = os.environ.get("SLACK_METABASE_REPORTING")
