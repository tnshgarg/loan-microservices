import os

from flask import Flask


def create_kyc_app(script_info=None):
    app = Flask("kyc_app")
    app_settings = os.getenv("APP_SETTINGS", "media_processing.config.DevelopmentConfig")
    app.config.from_object(app_settings)
    api_url_prefix = f"/{app.config['STAGE']}/{app.config['MICROSERVICE_NAME']}"
    from media_processing.api.ping import ping_blueprint
    from media_processing.api.kyc.aadhaar import aadhaar_ocr_blueprint
    
    app.register_blueprint(ping_blueprint)
    app.register_blueprint(aadhaar_ocr_blueprint,url_prefix=api_url_prefix)
    
    return app
