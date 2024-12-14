# backend/services/text_to_speech.py
from openai import AsyncOpenAI
import os
from pathlib import Path
import tempfile

class AudioService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.temp_dir = Path(tempfile.gettempdir()) / "podcast-audio"
        self.temp_dir.mkdir(exist_ok=True)

    async def create_audio(self, text: str, title: str) -> str:
        """
        Convert text to speech and return the file path
        """
        try:
            # Generate unique filename
            filename = f"audio_{hash(text)}.mp3"
            temp_path = self.temp_dir / filename

            # Generate speech using OpenAI
            response = await self.client.audio.speech.create(
                model="tts-1-hd",
                voice="echo",
                input=text
            )

            # Write the binary content to file using standard file operations
            with open(temp_path, 'wb') as f:
                f.write(response.content)
            
            return str(temp_path)

        except Exception as e:
            print(f"Error creating audio: {str(e)}")
            raise e