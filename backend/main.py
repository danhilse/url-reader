# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from bs4 import BeautifulSoup
import httpx
import re
from services.text_to_speech import AudioService
import os
import dotenv

from services.storage import S3Storage
from services.feed import RSSFeed
from datetime import datetime

# Load environment variables
dotenv.load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
audio_service = AudioService()

# Mount temp directory for serving audio files
app.mount("/audio", StaticFiles(directory=str(audio_service.temp_dir)), name="audio")

class UrlInput(BaseModel):
    url: str

async def scrape_content(url: str) -> str:
    """
    Scrape content from URL using httpx
    """
    async with httpx.AsyncClient() as client:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = await client.get(url, headers=headers, follow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for elem in soup.select('nav, footer, script, style, header'):
                elem.decompose()

            # Try to find the main content
            content_priorities = [
                soup.find('article'),
                soup.find('main'),
                soup.find(class_=re.compile(r'article|content|post|entry')),
                soup.find('body')
            ]
            
            main_content = next((content for content in content_priorities if content), None)
            
            if not main_content:
                raise HTTPException(status_code=400, detail="Could not find main content")

            # Extract text from relevant tags
            content_parts = []
            
            # Get title first
            title = soup.find('title')
            if title:
                content_parts.append(f"# {title.get_text(strip=True)}\n\n")
            
            # Get meta description
            meta_desc = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'property': 'og:description'})
            if meta_desc and meta_desc.get('content'):
                content_parts.append(f"*{meta_desc.get('content')}*\n\n")

            # Process main content
            for tag in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'blockquote']):
                text = tag.get_text(strip=True)
                if text:
                    if tag.name.startswith('h'):
                        level = int(tag.name[1])
                        content_parts.append(f"{'#' * level} {text}\n\n")
                    elif tag.name == 'blockquote':
                        content_parts.append(f"> {text}\n\n")
                    else:
                        content_parts.append(f"{text}\n\n")

            return "".join(content_parts)

        except httpx.HTTPError as e:
            raise HTTPException(status_code=400, detail=f"Error fetching URL: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scrape")
async def scrape_url(input: UrlInput):
    try:
        # First scrape the content
        content = await scrape_content(input.url)
        
        # Create audio version
        title = content.split('\n')[0].replace('#', '').strip() if content else "Untitled Article"
        
        # Get first 1000 characters for audio preview
        preview_text = ' '.join(content.split()[:100])  # First 100 words
        
        audio_path = await audio_service.create_audio(preview_text, title)
        
        # Convert file path to URL
        audio_filename = os.path.basename(audio_path)
        audio_url = f"/audio/{audio_filename}"
        
        return {
            "content": content,
            "audio_url": audio_url
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error in scrape_url: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Modify your convert_url endpoint to include RSS feed updates
@app.post("/api/convert")
async def convert_url(input: UrlInput):
    try:
        # Scrape content and get metadata
        content = await scrape_content(input.url)
        
        # Extract title and description
        title = content.split('\n')[0].replace('#', '').strip() if content else "Untitled Article"
        description = content.split('\n')[2].strip() if len(content.split('\n')) > 2 else ""
        
        # Create audio and upload to S3
        audio_path = await audio_service.create_audio(content, title)
        audio_url = await storage_service.upload_audio(audio_path, title)
        
        # Create RSS item
        new_item = {
            'title': title,
            'description': description,
            'pub_date': feed_service.format_date(datetime.now()),
            'audio_url': audio_url,
            'source_url': input.url,
            'file_size': os.path.getsize(audio_path)
        }
        
        # Generate updated RSS feed
        feed_xml = feed_service.generate_feed([new_item])  # For now, just show latest
        
        # Save feed XML to temp file for development
        feed_path = os.path.join(audio_service.temp_dir, 'feed.xml')
        with open(feed_path, 'w', encoding='utf-8') as f:
            f.write(feed_xml)
        
        return {
            "status": "success",
            "content": content,
            "audio_url": audio_url,
            "feed_url": "/audio/feed.xml"  # Accessible via your static files mount
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}