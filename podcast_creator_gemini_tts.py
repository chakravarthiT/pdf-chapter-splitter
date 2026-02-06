#!/usr/bin/env python3
"""
Podcast Creator - Gemini 2.5 Flash TTS Version
Extracts text from PDF, creates a summary, and converts to audio using Gemini 2.5 Flash TTS
For more natural and nuanced audio output with better emotion and tone
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

import google.generativeai as genai

from src.pdf_processor import PDFProcessor


class PodcastCreatorGeminiTTS:
    """Podcast creator using two Gemini 2.5 Flash models: one for summary, one for TTS"""
    
    def __init__(self, api_key: str):
        """Initialize with API key and two models"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")  # For summary
        self.tts_model = genai.GenerativeModel("gemini-2.5-flash-preview-tts")  # For audio generation
    
    def extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        print(f"📖 Reading PDF: {pdf_path}")
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        
        processor = PDFProcessor(pdf_bytes, pdf_path.name)
        full_text = processor.extract_full_text()
        
        print(f"✅ Extracted {len(full_text)} characters from PDF")
        return full_text
    
    def create_summary(self, text: str, max_length: int = 2000) -> str:
        """Create a concise summary from PDF text using Gemini 2.5 Flash"""
        print("🤖 Creating summary with Gemini 2.5 Flash...")
        
        prompt = f"""You are a professional podcast writer and narrator. Create a compelling and engaging podcast script summary from the following text.

The summary should:
1. Be conversational and engaging (as if spoken aloud naturally)
2. Capture the key points and main ideas
3. Be approximately {max_length} characters long
4. Have a clear beginning, middle, and end
5. Use simple, expressive language that's easy to understand
6. Include natural transitions between topics
7. Add some enthusiasm and emotion to make it engaging for listeners
8. Use variations in sentence structure to keep it interesting

TEXT TO SUMMARIZE:
{text[:5000]}  # Limit input to first 5000 chars for API efficiency

Create an engaging podcast script that a professional narrator would deliver naturally:"""
        
        response = self.model.generate_content(prompt)
        summary = response.text
        
        print(f"✅ Summary created ({len(summary)} characters)")
        return summary
    
    def create_podcast_audio(self, text: str, output_path: str) -> bool:
        """
        Create audio from text using Gemini 2.5 Flash TTS model
        Uses the dedicated TTS model for high-quality audio narration
        """
        print(f"🎙️ Converting to audio with Gemini 2.5 Flash TTS model...")
        
        try:
            # Prepare the output path
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create a prompt for the TTS model
            prompt = f"""You are a professional podcast narrator with expert voice acting skills. 
Generate a high-quality audio narration of this podcast script.
            
The narration should:
1. Sound natural and conversational
2. Have appropriate pacing and pauses between sentences
3. Use varied intonation to express emotion and emphasis
4. Be professional yet engaging for listeners
5. Include natural breathing pauses
6. Output as high-quality MP3 audio

Podcast script to narrate:

{text}"""
            
            print("⏳ Generating audio with Gemini 2.5 Flash TTS model...")
            
            # Generate audio using the TTS model
            response = self.tts_model.generate_content(
                prompt,
                stream=False
            )
            
            # Extract audio from response
            if hasattr(response, 'audio_content') and response.audio_content:
                with open(output_path, "wb") as audio_file:
                    audio_file.write(response.audio_content)
                print(f"✅ Audio saved: {output_path}")
                print(f"📁 File size: {output_path.stat().st_size / 1024:.2f} KB")
                return True
            elif hasattr(response, 'content') and response.content:
                # Try to extract audio data from content
                if isinstance(response.content, bytes):
                    with open(output_path, "wb") as audio_file:
                        audio_file.write(response.content)
                    print(f"✅ Audio saved: {output_path}")
                    print(f"📁 File size: {output_path.stat().st_size / 1024:.2f} KB")
                    return True
            
            # Debug: Check response details
            print(f"🔍 TTS Response type: {type(response)}")
            if hasattr(response, 'text'):
                print(f"🔍 Response text: {response.text[:300]}")
            print(f"🔍 Response attributes: {[attr for attr in dir(response) if not attr.startswith('_')]}")
            
            print("❌ TTS model did not return audio content")
            print("⚠️ Make sure your API key has access to gemini-2.5-flash-tts model")
            return False
                
        except Exception as e:
            print(f"❌ Error during TTS generation: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_podcast(self, pdf_path: str, output_dir: str = "podcasts") -> str:
        """Complete pipeline: PDF -> Summary -> Audio (using Gemini 2.5 Flash TTS)"""
        print("\n" + "="*60)
        print("🎙️ PODCAST CREATOR - GEMINI 2.5 FLASH TTS VERSION")
        print("="*60 + "\n")
        
        try:
            # Step 1: Extract text from PDF
            text = self.extract_pdf_text(pdf_path)[:10000]  # Limit to first 10k chars
            
            # Step 2: Create summary with Gemini 2.5 Flash
            summary = self.create_summary(text)
            
            # Step 3: Save summary
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True)
            
            pdf_name = Path(pdf_path).stem
            summary_path = output_dir / f"{pdf_name}_summary.txt"
            with open(summary_path, "w") as f:
                f.write(summary)
            print(f"💾 Summary saved: {summary_path}")
            
            # Step 4: Convert to audio using Gemini 2.5 Flash TTS
            audio_path = output_dir / f"{pdf_name}_podcast.mp3"
            success = self.create_podcast_audio(summary, str(audio_path))
            
            if success:
                print("\n" + "="*60)
                print("✅ Podcast creation completed successfully!")
                print("="*60)
            else:
                print("\n" + "="*60)
                print("⚠️ Summary created but audio generation had issues")
                print("="*60)
            
            return str(summary_path)
        
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return ""


def main():
    """Main entry point"""
    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not set in environment")
        print("Please set: export GEMINI_API_KEY='your-key-here'")
        sys.exit(1)
    
    # Get PDF path from command line or use default
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "sample.pdf"
    
    # Create podcast with Gemini TTS
    creator = PodcastCreatorGeminiTTS(api_key)
    creator.create_podcast(pdf_path)


if __name__ == "__main__":
    main()
