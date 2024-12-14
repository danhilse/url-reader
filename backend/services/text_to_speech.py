# backend/services/text_to_speech.py
from openai import AsyncOpenAI
import os
from pathlib import Path
import tempfile
import re
from pydub import AudioSegment

class AudioService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.temp_dir = Path(tempfile.gettempdir()) / "podcast-audio"
        self.temp_dir.mkdir(exist_ok=True)
        self.chunk_size = 4000  # Slightly less than 4096 to account for any extra characters

    def split_text(self, text: str) -> list[str]:
        """
        Split text into chunks that respect sentence boundaries and stay within OpenAI's limit
        """
        # Split into sentences (basic implementation)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            # If adding this sentence would exceed chunk size, start a new chunk
            if len(current_chunk) + len(sentence) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence

        # Add the last chunk if it exists
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    async def create_audio(self, text: str, title: str) -> str:
        """
        Convert text to speech, handling long texts by splitting into chunks
        """
        try:
            # Generate unique filename for final output
            filename = f"audio_{hash(text)}.mp3"
            final_path = self.temp_dir / filename

            # Split text into chunks if necessary
            chunks = self.split_text(text)
            
            if len(chunks) == 1:
                # If only one chunk, process normally
                response = await self.client.audio.speech.create(
                    model="tts-1-hd",
                    voice="echo",
                    input=chunks[0]
                )
                
                with open(final_path, 'wb') as f:
                    f.write(response.content)
                    
            else:
                # Process multiple chunks and combine
                temp_files = []
                combined = AudioSegment.empty()

                for i, chunk in enumerate(chunks):
                    # Generate audio for chunk
                    response = await self.client.audio.speech.create(
                        model="tts-1-hd",
                        voice="echo",
                        input=chunk
                    )
                    
                    # Save chunk to temporary file
                    chunk_path = self.temp_dir / f"temp_chunk_{i}_{filename}"
                    with open(chunk_path, 'wb') as f:
                        f.write(response.content)
                    
                    temp_files.append(chunk_path)
                    
                    # Add to combined audio with a small pause between chunks
                    chunk_audio = AudioSegment.from_mp3(chunk_path)
                    silence = AudioSegment.silent(duration=500)  # 500ms pause
                    combined += chunk_audio + silence
                
                # Export final combined audio
                combined.export(final_path, format="mp3")
                
                # Clean up temporary chunk files
                for temp_file in temp_files:
                    try:
                        os.remove(temp_file)
                    except:
                        pass

            return str(final_path)

        except Exception as e:
            print(f"Error creating audio: {str(e)}")
            raise e