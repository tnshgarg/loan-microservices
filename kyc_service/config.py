
import json
import os


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
class SlackWebhooks:
    DEV_CHANNEL = os.environ.get("SLACK_DEV_CHANNEL")
    GITHUB_ACTIONS = os.environ.get("SLACK_GITHUB_ACTIONS")
    METABASE_REPORTING = os.environ.get("SLACK_METABASE_REPORTING")
