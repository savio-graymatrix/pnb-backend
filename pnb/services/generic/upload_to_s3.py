import boto3
from botocore.exceptions import ClientError
import os
from pnb import SETTINGS

s3_client = boto3.client(
    "s3",
    region_name=SETTINGS.AWS_REGION,
    aws_access_key_id=SETTINGS.AWS_ACCESS_KEY,
    aws_secret_access_key=SETTINGS.AWS_SECRET_KEY,
)


def upload_to_s3(file_bytes: bytes, filename: str, content_type: str) -> str:
    try:
        s3_client.put_object(
            Bucket=SETTINGS.AWS_BUCKET,
            Key=filename,
            Body=file_bytes,
            ContentType=content_type,
        )
        return f"{SETTINGS.S3_CDN_URL}/{filename}"
    except ClientError as e:
        raise RuntimeError(f"S3 Upload Failed: {e}")
