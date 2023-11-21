from dal.logger import get_app_logger
from kyc_service.config import Config


app_logger = get_app_logger("kyc-service", Config.STAGE)
