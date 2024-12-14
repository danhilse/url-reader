# URL to Podcast Converter: Backend Documentation

## Overview
A FastAPI backend service that converts web articles into audio podcasts using OpenAI's Text-to-Speech API. The system scrapes web content, processes it, generates audio, and maintains a podcast RSS feed.

## System Architecture

### Core Components
```
backend/
├── main.py                  # FastAPI application and endpoints
├── requirements.txt         # Project dependencies
└── services/
    ├── text_to_speech.py    # OpenAI TTS integration
    ├── storage.py           # AWS S3 operations
    ├── feed.py             # RSS feed management
    └── prompt.py           # Text processing utilities
```

## Setup and Installation

### Prerequisites
- Python 3.11+
- FFmpeg (required for audio processing)
- AWS account with S3 and CloudFront configured
- OpenAI API key

### Environment Variables
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_key

# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_BUCKET_NAME=your_bucket_name
CLOUDFRONT_DOMAIN=your_cloudfront_domain
```

### Installation Steps
1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables
5. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```

## Core Services

### Audio Service (`text_to_speech.py`)
Handles text-to-speech conversion using OpenAI's API.

Key features:
- Uses OpenAI's TTS-1-HD model for high-quality audio
- Chunks long text to handle OpenAI's 4096 character limit
- Combines audio segments with natural pauses
- Maintains temporary file storage

```python
await audio_service.create_audio(text: str, title: str) -> str
```

### Storage Service (`storage.py`)
Manages AWS S3 interactions for audio file storage.

Key features:
- Uploads audio files to S3
- Generates CloudFront URLs
- Handles file naming and metadata
- Manages content types

### Feed Service (`feed.py`)
Manages the podcast RSS feed generation and updates.

Key features:
- Creates and maintains RSS 2.0 feed structure
- Handles iTunes podcast tags
- Manages episode entries
- Syncs feed with S3

## API Endpoints

### Content Extraction
```http
POST /api/extract
Content-Type: application/json

{
    "url": "string"
}
```
Returns extracted article content and title.

### Streaming Content Extraction
```http
GET /api/extract/stream?url=string
```
Streams content word-by-word with formatting metadata. Uses Server-Sent Events (SSE).

Event types:
- `init`: Total word count
- `word`: Individual word content
- `lineBreak`: Line break indicators
- `complete`: Stream completion
- `error`: Error information

### Audio Generation
```http
POST /api/generate-audio
Content-Type: application/json

{
    "url": "string"
}
```
Generates audio from article content.

Response:
```json
{
    "audio_url": "string"  // Local URL for immediate playback
}
```

### RSS Feed Access
```http
GET /api/feed
```
Returns the podcast RSS feed XML.

### Health Check
```http
GET /api/health
```
Returns service health status.

## Content Processing

### Text Processing Limits
- Maximum content length: 16,000 characters
- Maximum TTS chunk size: 4,000 characters
- Content beyond limits is truncated with notification

### Content Extraction Rules
- Preserves document structure (headings, paragraphs)
- Removes navigation, footers, scripts
- Excludes images and their alt text
- Prioritizes main content areas

## Error Handling

The API uses standard HTTP status codes:
- 200: Success
- 400: Invalid request (malformed URL, content not found)
- 500: Server error (TTS failure, S3 upload error)

All errors include detailed messages in the response:
```json
{
    "detail": "Error description"
}
```

## Best Practices

### Audio File Management
- Use unique filenames based on content hash
- Clean up temporary files after processing
- Implement proper error handling for file operations

### Content Processing
- Respect HTML document structure
- Handle text encoding properly
- Validate URLs and content length
- Implement proper character escaping

### AWS Integration
- Use CloudFront for content delivery
- Implement proper CORS settings
- Handle S3 upload retries
- Manage file permissions carefully

## Development Notes

### Local Development
- Use `uvicorn main:app --reload` for auto-reloading
- Set up local S3 endpoints for testing
- Monitor `/tmp` directory for audio files
- Use proper CORS settings for local frontend

### Testing
- Test with various article lengths
- Verify audio file generation
- Check RSS feed validity
- Monitor S3 upload success
- Validate CloudFront URLs

### Monitoring
- Check logs for TTS errors
- Monitor temporary file cleanup
- Watch S3 upload success rates
- Verify RSS feed updates

## Deployment

### Requirements
- Python 3.11+ runtime
- FFmpeg installation
- Proper environment configuration
- AWS credentials and permissions
- Adequate storage space for temporary files

### Testing the Deployment
1. Verify health check endpoint
2. Test content extraction
3. Validate audio generation
4. Check RSS feed updates
5. Confirm CloudFront access
