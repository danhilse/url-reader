import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class ContentPrompts:
    """Storage class for all content-related prompts"""
    
    @staticmethod
    def get_audio_adaptation_prompt(article_content: str) -> str:
        """Returns the prompt for audio content adaptation"""
        return f'''You are an expert in content adaptation, specializing in converting written articles into audio format. Your task is to analyze the following article and optimize it for voice conversion while keeping it as close to the original as possible.

Here is the article content:

<article_content>
{article_content}
</article_content>

Please follow these steps to analyze and revise the article:

1. Read through the article carefully.

2. Analyze the content for the following elements that might not translate well to audio format:

   a) Visual References: Identify mentions of images, charts, tables, or any visual elements.
   b) Complex Sentence Structures: Locate long or complex sentences.
   c) Text-Specific Features: Highlight bullet points, numbered lists, hyperlinks, or formatting instructions.
   d) Redundancies and Repetitions: Detect any repetitive content.
   e) Interactive Elements: Locate questions, calls to action, or prompts.

3. For each element identified, suggest minimal adjustments to make the content more suitable for audio format. Remember to keep changes to a minimum while ensuring the content flows well when listened to.

4. Based on your analysis, create a revised version of the article that is optimized for voice conversion.

Before providing the final revised article, wrap your analysis inside <content_adaptation_analysis> tags. For each category:

a) Visual References: Quote the relevant parts and suggest audio descriptions.
b) Complex Sentences: Rewrite them in a simpler form.
c) Text-Specific Features: Suggest audio-friendly alternatives.
d) Redundancies: Highlight repetitive phrases and suggest consolidations.
e) Interactive Elements: Adapt them for audio format.

This will ensure a thorough interpretation of the content and justify any changes made. It's OK for this section to be quite long.

After your analysis, present the revised article within <revised_article> tags. The revised article should flow smoothly and naturally for listeners while staying as close as possible to the original content.'''

def make_api_call(content: str, max_retries: int = 3) -> dict:
    """
    Make API call to OpenAI with retry logic
    
    Args:
        content: The article content to analyze
        max_retries: Maximum number of retry attempts
        
    Returns:
        dict: Parsed response containing analysis and revised content
    """
    retries = 0
    
    while retries <= max_retries:
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert content adaptation assistant."},
                    {"role": "user", "content": ContentPrompts.get_audio_adaptation_prompt(content)}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            response_text = response.choices[0].message.content
            
            # Extract analysis and revised content using tags
            analysis = extract_between_tags(response_text, "content_adaptation_analysis")
            revised = extract_between_tags(response_text, "revised_article")
            
            return {
                "analysis": analysis,
                "revised_content": revised,
                "original_response": response_text
            }
            
        except Exception as e:
            retries += 1
            print(f"Attempt {retries} failed with error: {str(e)}")
            if retries > max_retries:
                raise
            time.sleep(2)
    
    return None

def extract_between_tags(text: str, tag_name: str) -> str:
    """
    Extract content between XML-style tags
    
    Args:
        text: The text to search in
        tag_name: The name of the tag to extract content from
        
    Returns:
        str: Content between the tags, or empty string if not found
    """
    import re
    pattern = f"<{tag_name}>(.*?)</{tag_name}>"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else ""

def analyze_content(article_content: str) -> dict:
    """
    Main function to analyze and adapt content for audio
    
    Args:
        article_content: The original article content
        
    Returns:
        dict: Analysis results and revised content
    """
    try:
        result = make_api_call(article_content)
        if result:
            return {
                "success": True,
                "analysis": result["analysis"],
                "revised_content": result["revised_content"],
                "original_response": result["original_response"]
            }
        else:
            return {
                "success": False,
                "error": "Failed to get valid response from API"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

