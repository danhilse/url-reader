# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse  # Add StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from bs4 import BeautifulSoup
import httpx
import re
from services.text_to_speech import AudioService
from services.storage import S3Storage
from services.feed import RSSFeed
import os
import dotenv
import asyncio
import json

# Load environment variables
dotenv.load_dotenv()

app = FastAPI()


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://url-reader.vercel.app",  # Your Vercel domain
        "https://url-reader-git-master-danhilses-projects.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Initialize services in correct order
audio_service = AudioService()
storage_service = S3Storage()
feed_service = RSSFeed(str(audio_service.temp_dir))

# Mount temp directory for serving audio files
app.mount("/audio", StaticFiles(directory=str(audio_service.temp_dir)), name="audio")

class UrlInput(BaseModel):
    url: str

MAX_CONTENT_LENGTH = 16000
TRUNCATION_MESSAGE = "\n\n[Article truncated due to length]"

async def scrape_content(url: str) -> str:
    """
    Scrape content from URL using httpx, removing images and alt text.
    Content is truncated if it exceeds MAX_CONTENT_LENGTH.
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

            # Remove all images and their alt text
            for img in soup.find_all('img'):
                img.decompose()
            
            # Remove figure elements (often contain images with captions)
            for figure in soup.find_all('figure'):
                figure.decompose()
                
            # Remove picture elements (responsive images)
            for picture in soup.find_all('picture'):
                picture.decompose()
                
            # Remove svg elements
            for svg in soup.find_all('svg'):
                svg.decompose()

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
            
            # Always include title if available (don't count towards length limit)
            title = soup.find('title')
            title_text = f"# {title.get_text(strip=True)}\n\n" if title else ""
            
            # Get meta description (don't count towards length limit)
            meta_desc = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'property': 'og:description'})
            meta_text = f"*{meta_desc.get('content')}*\n\n" if meta_desc and meta_desc.get('content') else ""

            # Process main content with length tracking
            current_length = 0
            exceeded_limit = False
            
            for tag in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'blockquote']):
                text = tag.get_text(strip=True)
                if text:
                    formatted_text = ""
                    if tag.name.startswith('h'):
                        level = int(tag.name[1])
                        formatted_text = f"{'#' * level} {text}\n\n"
                    elif tag.name == 'blockquote':
                        formatted_text = f"> {text}\n\n"
                    else:
                        formatted_text = f"{text}\n\n"
                    
                    # Check if adding this would exceed limit
                    if current_length + len(formatted_text) > MAX_CONTENT_LENGTH:
                        exceeded_limit = True
                        break
                        
                    content_parts.append(formatted_text)
                    current_length += len(formatted_text)

            # Combine all parts
            content = title_text + meta_text + "".join(content_parts)
            
            # Add truncation message if needed
            if exceeded_limit:
                content = content.rstrip() + TRUNCATION_MESSAGE

            # Clean up any double spaces or extra newlines
            content = re.sub(r'\n{3,}', '\n\n', content)
            content = re.sub(r' {2,}', ' ', content)
            
            return content.strip()

        except httpx.HTTPError as e:
            raise HTTPException(status_code=400, detail=f"Error fetching URL: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
@app.post("/api/scrape")
async def scrape_url(input: UrlInput):
    try:
        # First scrape the content
        content = await scrape_content(input.url)
        
        # Extract title
        title = content.split('\n')[0].replace('#', '').strip() if content else "Untitled Article"
        
        # Get preview text for audio (first 100 words)
        preview_text = ' '.join(content.split()[:100])
        
        # Create audio file locally
        audio_path = await audio_service.create_audio(preview_text, title)
        
        # Upload to S3
        audio_url = await storage_service.upload_audio(audio_path, title)
        
        # Update RSS feed
        feed_service.add_item(title, audio_url, input.url)
        
        # Get local audio URL for immediate playback
        audio_filename = os.path.basename(audio_path)
        local_audio_url = f"/audio/{audio_filename}"
        
        return {
            "content": content,
            "audio_url": local_audio_url  # Return local URL for immediate playback
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
        # First scrape the content
        content = await scrape_content(input.url)
        
        # Extract title
        title = content.split('\n')[0].replace('#', '').strip() if content else "Untitled Article"
        
        # Create audio file locally
        audio_path = await audio_service.create_audio(content, title)
        
        # Upload to S3
        audio_url = await storage_service.upload_audio(audio_path, title)
        
        # Update RSS feed
        feed_service.add_item(title, audio_url, input.url)
        
        return {
            "status": "success",
            "content": content,
            "audio_url": audio_url,
            "feed_url": "/audio/feed.xml"  # Accessible via your static files mount
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error in convert_url: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Add a new endpoint to get the RSS feed
@app.get("/api/feed")
async def get_feed():
    feed_path = os.path.join(audio_service.temp_dir, 'feed.xml')
    if os.path.exists(feed_path):
        return FileResponse(feed_path, media_type='application/xml')
    raise HTTPException(status_code=404, detail="Feed not found")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/extract")
async def extract_content(input: UrlInput):
    """New endpoint that only handles text extraction"""
    try:
        content = await scrape_content(input.url)
        title = content.split('\n')[0].replace('#', '').strip() if content else "Untitled Article"
        
        return {
            "content": content,
            "title": title
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error in extract_content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-audio")
async def generate_audio(input: UrlInput):
    """New endpoint that handles audio generation"""
    try:
        content = await scrape_content(input.url)
        title = content.split('\n')[0].replace('#', '').strip() if content else "Untitled Article"
        
        # Create audio file locally
        audio_path = await audio_service.create_audio(content, title)
        
        # Upload to S3
        audio_url = await storage_service.upload_audio(audio_path, title)
        
        # Update RSS feed
        feed_service.add_item(title, audio_url, input.url)
        
        # Get local audio URL for immediate playback
        audio_filename = os.path.basename(audio_path)
        local_audio_url = f"/audio/{audio_filename}"
        
        return {
            "audio_url": local_audio_url
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error in generate_audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.get("/api/extract/stream")
async def extract_content_stream(url: str):
    """Stream the content word by word, respecting markdown formatting"""
    async def generate():
        try:
            content = await scrape_content(url)
            paragraphs = content.split('\n\n')
            total_words = sum(len(p.split()) for p in paragraphs)
            
            yield f"data: {json.dumps({'type': 'init', 'total': total_words})}\n\n"
            
            word_index = 0
            for paragraph in paragraphs:
                lines = paragraph.split('\n')
                for i, line in enumerate(lines):
                    # Detect header level
                    header_level = 0
                    if line.strip().startswith('#'):
                        header_level = len(line.split()[0])  # Count # symbols
                        line = ' '.join(line.split()[1:])  # Remove # symbols
                    
                    words = line.split()
                    for word in words:
                        data = {
                            'type': 'word',
                            'content': word,
                            'index': word_index,
                            'lineBreak': False,
                            'headerLevel': header_level if header_level else None
                        }
                        yield f"data: {json.dumps(data)}\n\n"
                        word_index += 1
                        await asyncio.sleep(0.01)
                    
                    # Add line break if this isn't the last line in the paragraph
                    if i < len(lines) - 1:
                        data = {
                            'type': 'lineBreak',
                            'index': word_index - 1,
                            'isParagraphBreak': False,
                            'headerLevel': header_level if header_level else None
                        }
                        yield f"data: {json.dumps(data)}\n\n"
                
                # Add paragraph break after each paragraph except the last one
                if paragraph != paragraphs[-1]:
                    data = {
                        'type': 'lineBreak',
                        'index': word_index - 1,
                        'isParagraphBreak': True,
                        'headerLevel': None
                    }
                    yield f"data: {json.dumps(data)}\n\n"
            
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(), 
        media_type="text/event-stream"
    )