import datetime

import boto3


class S3ReportService:

    def __init__(self, stage, logger) -> None:
        self.stage = stage
        self.logger = logger

    def upload(self, data, pan, provider, bureau):
        current_timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        s3 = boto3.client('s3')
        s3_bucket = f"{self.stage}-unipe-bureau-pull"
        s3_key = f"{pan}/{provider}/{bureau}/{current_timestamp}.zlib"
        s3_body = data
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=s3_body)

        return
