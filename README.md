# URL to Podcast Converter

Convert web articles into audio podcasts with AI narration. This application scrapes articles, generates high-quality audio using OpenAI's Text-to-Speech API, and creates a podcast feed you can subscribe to in your favorite podcast app.

![Demo of URL to Podcast Converter](%2A%20public/demo.gif)

## Prerequisites

- Node.js 18.0 or higher
- Python 3.11 or higher
- FFmpeg
- AWS Account with S3 and CloudFront
- OpenAI API key

## Installation

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/your-username/url-to-podcast.git
cd url-to-podcast/backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the backend directory:
```bash
OPENAI_API_KEY=your_openai_key
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_BUCKET_NAME=your_bucket_name
CLOUDFRONT_DOMAIN=your_cloudfront_domain
```

5. Start the backend server:
```bash
uvicorn main:app --reload
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd ../frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

## AWS Configuration

1. Create an S3 bucket:
   - Enable public access
   - Configure CORS for your domain

2. Set up CloudFront:
   - Create a distribution pointing to your S3 bucket
   - Enable HTTPS
   - Configure appropriate cache behaviors

3. Update your bucket policy:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-bucket/*"
        }
    ]
}
```

## Usage

1. Enter an article URL in the input field
2. Watch as the content is extracted and formatted in real-time
3. Listen to the generated audio directly in the browser
4. Copy the RSS feed URL to subscribe in your podcast app

## Development

### Backend Development

The backend uses FastAPI with the following structure:
```
backend/
├── services/          
│   ├── text_to_speech.py  # OpenAI TTS integration
│   ├── storage.py      # S3 storage management
│   └── feed.py         # RSS feed generation
├── main.py             # FastAPI endpoints
└── requirements.txt   
```

### Frontend Development

The frontend uses Next.js 14 with TypeScript:
```
frontend/
├── app/                 
│   └── page.tsx         # Main page component
├── components/         
│   ├── ui/             # shadcn components
│   └── audio-player.tsx # Audio playback
└── lib/                # Utilities
```

## Acknowledgments

- OpenAI for the Text-to-Speech API
- [shadcn/ui](https://ui.shadcn.com/) for the component library
- All contributors and supporters
