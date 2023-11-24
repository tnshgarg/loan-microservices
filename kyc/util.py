from dal.logger import get_app_logger
from kyc.config import Config


app_logger = get_app_logger("kyc-service", Config.STAGE)
