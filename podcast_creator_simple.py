#!/usr/bin/env python3
"""
Podcast Creator - Simple Version
Extracts text from PDF, creates a summary, and converts to audio using Gemini Flash TTS
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

import google.generativeai as genai
from gtts import gTTS

from src.pdf_processor import PDFProcessor


class PodcastCreatorSimple:
    """Simple podcast creator using Gemini Flash for TTS"""
    
    def __init__(self, api_key: str):
        """Initialize with API key"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.tts_model = "gemini-2.5-flash"  # Flash model for TTS
    
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
        """Create a concise summary from PDF text using Gemini"""
        print("🤖 Creating summary with Gemini...")
        
        prompt = f"""You are a professional podcast writer. Create a compelling and engaging podcast script summary from the following text.

The summary should:
1. Be conversational and engaging (as if spoken aloud)
2. Capture the key points and main ideas
3. Be approximately {max_length} characters long
4. Have a clear beginning, middle, and end
5. Use simple language that's easy to understand
6. Include transitions between topics

TEXT TO SUMMARIZE:
{text[:5000]}  # Limit input to first 5000 chars for API efficiency

Create an engaging podcast script:"""
        
        response = self.model.generate_content(prompt)
        summary = response.text
        
        print(f"✅ Summary created ({len(summary)} characters)")
        return summary
    
    def text_to_speech(self, text: str, output_path: str) -> bool:
        """Convert text to speech using gTTS (Google Text-to-Speech)"""
        print(f"🎙️ Converting text to speech with gTTS...")
        
        try:
            # Use gTTS for text-to-speech conversion
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Create output directory if needed
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save the audio file
            tts.save(str(output_path))
            
            print(f"✅ Audio saved: {output_path}")
            print(f"📁 File size: {output_path.stat().st_size / 1024:.2f} KB")
            
            return True
        except Exception as e:
            print(f"❌ Error during TTS: {e}")
            print("📌 Make sure you have internet connection for gTTS")
            return False
    
    def create_podcast(self, pdf_path: str, output_dir: str = "podcasts") -> str:
        """Complete pipeline: PDF -> Summary -> Audio"""
        print("\n" + "="*60)
        print("🎙️ PODCAST CREATOR - SIMPLE VERSION")
        print("="*60 + "\n")
        
        try:
            # Step 1: Extract text from PDF
            text = self.extract_pdf_text(pdf_path)[:1000]  # Limit to first 10k chars for processing
            
            # Step 2: Create summary
            summary = self.create_summary(text)
            
            # Step 3: Save summary
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True)
            
            pdf_name = Path(pdf_path).stem
            summary_path = output_dir / f"{pdf_name}_summary.txt"
            with open(summary_path, "w") as f:
                f.write(summary)
            print(f"💾 Summary saved: {summary_path}")
            
            # Step 4: Convert to audio (requires additional API)
            audio_path = output_dir / f"{pdf_name}_podcast.mp3"
            self.text_to_speech(summary, str(audio_path))
            
            print("\n" + "="*60)
            print("✅ Podcast creation completed!")
            print("="*60)
            
            return str(summary_path)
        
        except Exception as e:
            print(f"❌ Error: {e}")
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
    
    # Create podcast
    creator = PodcastCreatorSimple(api_key)
    creator.create_podcast(pdf_path)


if __name__ == "__main__":
    main()
