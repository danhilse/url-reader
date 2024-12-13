# backend/services/storage.py
import boto3
from datetime import datetime
import os
from urllib.parse import quote

class S3Storage:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.bucket_name = os.getenv('AWS_BUCKET_NAME')

    async def upload_audio(self, file_path: str, title: str) -> str:
        # Create a URL-safe filename from the title
        safe_title = quote(title.lower().replace(' ', '-'))
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        key = f"audio/{timestamp}-{safe_title}.mp3"

        # Upload file
        with open(file_path, 'rb') as file:
            self.s3_client.upload_fileobj(file, self.bucket_name, key)

        # Generate public URL
        url = f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
        return url

# backend/services/feed.py
from datetime import datetime
import xml.etree.ElementTree as ET
from typing import List, Dict
import os

class RSSFeed:
    def __init__(self):
        self.rss_template = {
            'title': 'URL to Podcast Converter',
            'description': 'AI-powered audio versions of web articles',
            'link': 'https://your-domain.com',  # Update this
            'language': 'en-us',
        }

    def generate_feed(self, items: List[Dict]) -> str:
        rss = ET.Element('rss', version='2.0')
        rss.set('xmlns:itunes', 'http://www.itunes.com/dtds/podcast-1.0.dtd')
        rss.set('xmlns:content', 'http://purl.org/rss/1.0/modules/content/')

        channel = ET.SubElement(rss, 'channel')
        
        # Add channel metadata
        for key, value in self.rss_template.items():
            elem = ET.SubElement(channel, key)
            elem.text = value

        # Add items
        for item in items:
            item_elem = ET.SubElement(channel, 'item')
            
            # Required elements
            title = ET.SubElement(item_elem, 'title')
            title.text = item['title']
            
            description = ET.SubElement(item_elem, 'description')
            description.text = item['description']
            
            pubDate = ET.SubElement(item_elem, 'pubDate')
            pubDate.text = item['pub_date']
            
            guid = ET.SubElement(item_elem, 'guid')
            guid.text = item['audio_url']
            guid.set('isPermaLink', 'true')
            
            # Enclosure for audio file
            enclosure = ET.SubElement(item_elem, 'enclosure')
            enclosure.set('url', item['audio_url'])
            enclosure.set('type', 'audio/mpeg')
            enclosure.set('length', str(item.get('file_size', 0)))
            
            # Optional elements
            if 'duration' in item:
                duration = ET.SubElement(item_elem, 'itunes:duration')
                duration.text = item['duration']
            
            if 'source_url' in item:
                source_link = ET.SubElement(item_elem, 'link')
                source_link.text = item['source_url']

        return ET.tostring(rss, encoding='unicode', method='xml')

    def format_date(self, dt: datetime) -> str:
        """Format datetime object to RFC 822 format for RSS"""
        return dt.strftime('%a, %d %b %Y %H:%M:%S +0000')