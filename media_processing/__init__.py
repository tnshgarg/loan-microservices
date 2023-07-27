import os

from flask import Flask
from media_processing.api.ping import ping_blueprint
from media_processing.api.kyc.aadhaar import aadhaar_ocr_blueprint

def create_app(script_info=None):
    app = Flask("media_processor")
    app_settings = os.getenv("APP_SETTINGS")
    app.config.from_object(app_settings)
    app.register_blueprint(ping_blueprint)
    app.register_blueprint(aadhaar_ocr_blueprint)
    return app
