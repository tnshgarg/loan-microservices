import datetime

import boto3
from botocore.exceptions import ClientError


class S3ReportService:

    def __init__(self, stage, logger) -> None:
        self.stage = stage
        self.logger = logger
        self.s3_client = boto3.client('s3')
        self.s3_bucket = f"{self.stage}-unipe-bureau-pull"

    def upload(self, data, pan, provider, bureau):
        current_timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        s3_key = f"{pan}/{provider}/{bureau}/{current_timestamp}.json"
        s3_body = data
        self.s3_client.put_object(
            Bucket=self.s3_bucket, Key=s3_key, Body=s3_body)
        return s3_key

    def create_presigned_url(self, s3_key, expiration=3600):
        # Generate a presigned URL for the S3 object
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.s3_bucket,
                    'Key': s3_key,
                },
                ExpiresIn=expiration,
            )
        except ClientError as e:
            self.logger.info("s3_presigned_url_client_error", extra={
                "error": str(e)
            })
            return None

        # The response contains the presigned URL
        return response
