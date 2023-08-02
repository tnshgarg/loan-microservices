import boto3
from botocore.exceptions import ClientError
import logging

from kyc_service.config import Config

CLOUDFRONT_URL = "https://d22ss3ef1t9wna.cloudfront.net/"


class S3UploadService:

    def __init__(self, bucket) -> None:
        self.bucket_name = bucket

    def upload(self, key, fd) -> (bool, str | None):
        s3_client = boto3.client('s3')
        try:
            fd.seek(0)
            response = s3_client.put_object(
                Body=fd.read(),
                Bucket=self.bucket_name,
                Key=Config.STAGE + "/" + key,
            )
            logging.info(response)
        except ClientError as e:
            logging.error(e)
            return (False, None)
        return (True, CLOUDFRONT_URL + Config.STAGE + "/" + key)
