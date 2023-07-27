import sys

from flask.cli import FlaskGroup
from media_processing import create_kyc_app

app = create_kyc_app()

cli = FlaskGroup(create_app=create_kyc_app)

if __name__ == "__main__":
    cli()