# backend/services/feed.py
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import boto3
from typing import List, Dict
import requests

class RSSFeed:
    def __init__(self, temp_dir: str):
        self.temp_dir = temp_dir
        self.feed_path = os.path.join(temp_dir, 'feed.xml')
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.bucket_name = os.getenv('AWS_BUCKET_NAME')
        # Add CloudFront domain
        self.cloudfront_domain = os.getenv('CLOUDFRONT_DOMAIN')  # e.g., 'dxxxxxxxxxxxx.cloudfront.net'
    
    def _get_file_size(self, url: str) -> int:
        """Get file size from URL using HEAD request"""
        try:
            response = requests.head(url)
            if response.status_code == 200:
                return int(response.headers.get('content-length', 0))
        except Exception as e:
            print(f"Error getting file size: {str(e)}")
        return 0

    def _get_cloudfront_url(self, s3_key: str) -> str:
        """Convert S3 key to CloudFront URL"""
        return f"https://{self.cloudfront_domain}/{s3_key}"
    
    # backend/services/feed.py
    def add_item(self, title: str, audio_url: str, source_url: str) -> None:
        # Get existing feed or create new one
        root = self._download_feed()
        channel = root.find('channel')
        
        # Add new item at the beginning of the channel
        item = ET.Element('item')
        channel.insert(0, item)
        
        # Ensure we're using CloudFront URLs
        if not audio_url.startswith(f"https://{self.cloudfront_domain}"):
            print(f"Warning: Audio URL is not using CloudFront domain: {audio_url}")
        
        ET.SubElement(item, 'title').text = title
        ET.SubElement(item, 'link').text = source_url
        ET.SubElement(item, 'guid', isPermaLink='true').text = audio_url
        ET.SubElement(item, 'pubDate').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # Add description
        ET.SubElement(item, 'description').text = f"Audio version of: {title}"
        
        # Add enclosure with file size
        file_size = self._get_file_size(audio_url)
        print(f"Audio file size: {file_size} bytes")
        
        enclosure = ET.SubElement(item, 'enclosure')
        enclosure.set('url', audio_url)
        enclosure.set('type', 'audio/mpeg')
        enclosure.set('length', str(file_size))
        
        # Save locally and upload to S3
        tree = ET.ElementTree(root)
        tree.write(self.feed_path, encoding='utf-8', xml_declaration=True)
        
        try:
            self.s3_client.upload_file(
                self.feed_path,
                self.bucket_name,
                'feed.xml',
                ExtraArgs={
                    'ContentType': 'application/xml'
                }
            )
            feed_url = f"https://{self.cloudfront_domain}/feed.xml"
            print(f"Updated feed at: {feed_url}")
        except Exception as e:
            print(f"Error uploading feed to S3: {str(e)}")
            raise e
    def _download_feed(self) -> ET.Element:
        """Download existing feed from S3 or create new one"""
        try:
            self.s3_client.download_file(self.bucket_name, 'feed.xml', self.feed_path)
            tree = ET.parse(self.feed_path)
            return tree.getroot()
        except:
            # Create new feed if doesn't exist
            root = ET.Element('rss', version='2.0')
            root.set('xmlns:itunes', 'http://www.itunes.com/dtds/podcast-1.0.dtd')
            channel = ET.SubElement(root, 'channel')
            
            # Add feed metadata with CloudFront URL
            ET.SubElement(channel, 'title').text = 'URL to Audio Feed'
            ET.SubElement(channel, 'link').text = self._get_cloudfront_url('feed.xml')
            ET.SubElement(channel, 'description').text = 'Audio versions of web articles'
            ET.SubElement(channel, 'language').text = 'en-us'
            
            # Add iTunes-specific tags
            ET.SubElement(channel, 'itunes:author').text = 'URL to Audio'
            ET.SubElement(channel, 'itunes:summary').text = 'Audio versions of web articles'
            ET.SubElement(channel, 'itunes:category').set('text', 'Technology')
            
            return root