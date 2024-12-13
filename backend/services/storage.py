# backend/services/storage.py
import boto3
import os
from datetime import datetime
import re
from urllib.parse import quote

class S3Storage:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.bucket_name = os.getenv('AWS_BUCKET_NAME')
        self.cloudfront_domain = os.getenv('CLOUDFRONT_DOMAIN')

    def _sanitize_filename(self, title: str) -> str:
        """Create a safe filename from title"""
        # Remove special characters and replace spaces with hyphens
        safe_title = re.sub(r'[:\\/.*?"<>|]', '', title)
        safe_title = safe_title.lower().replace(' ', '-')
        # Remove multiple hyphens
        safe_title = re.sub(r'-+', '-', safe_title)
        # Remove leading/trailing hyphens
        safe_title = safe_title.strip('-')
        return safe_title

    async def upload_audio(self, file_path: str, title: str) -> str:
        # Create safe filename
        safe_title = self._sanitize_filename(title)
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        key = f"audio/{timestamp}-{safe_title}.mp3"

        try:
            # Upload to S3
            self.s3_client.upload_file(
                file_path, 
                self.bucket_name, 
                key,
                ExtraArgs={
                    'ContentType': 'audio/mpeg'
                }
            )
            
            # Return CloudFront URL
            url = f"https://{self.cloudfront_domain}/{key}"
            print(f"Uploaded audio to CloudFront: {url}")
            return url
            
        except Exception as e:
            print(f"Error uploading to S3: {str(e)}")
            raise e