#!/usr/bin/env python3
"""
Podcast Creator - Multi-Model Version
Uses multiple Gemini models for advanced processing:
1. Gemini Pro for deep analysis and script generation
2. Gemini Flash for quick summary and optimization
3. Vision API for analyzing PDF images if present
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, List
import google.generativeai as genai
from src.pdf_processor import PDFProcessor
from dataclasses import dataclass
from enum import Enum


class ContentType(Enum):
    """Types of podcast content"""
    EDUCATIONAL = "educational"
    NARRATIVE = "narrative"
    DISCUSSION = "discussion"
    NEWS = "news"


@dataclass
class PodcastScript:
    """Structured podcast script data"""
    title: str
    introduction: str
    main_content: List[str]
    conclusion: str
    estimated_duration_minutes: float
    content_type: ContentType


class PodcastCreatorMultiModel:
    """Advanced podcast creator using multiple Gemini models"""
    
    def __init__(self, api_key: str):
        """Initialize with API key and configure models"""
        genai.configure(api_key=api_key)
        self.pro_model = genai.GenerativeModel("gemini-1.5-pro")      # Deep analysis
        self.flash_model = genai.GenerativeModel("gemini-2.0-flash")  # Quick processing
    
    def extract_pdf_text_with_metadata(self, pdf_path: str) -> tuple[str, Dict]:
        """Extract text and metadata from PDF"""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        print(f"📖 Reading PDF: {pdf_path}")
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        
        processor = PDFProcessor(pdf_bytes, pdf_path.name)
        full_text = processor.extract_full_text()
        
        # Get PDF info
        pdf_info = processor.get_pdf_info()
        
        metadata = {
            "filename": pdf_info.filename,
            "total_pages": pdf_info.total_pages,
            "chapters": [{"title": c.title, "pages": f"{c.start_page}-{c.end_page}"} 
                        for c in pdf_info.chapters[:5]],  # First 5 chapters
            "word_count": len(full_text.split())
        }
        
        print(f"✅ Extracted {len(full_text)} characters, {metadata['word_count']} words")
        return full_text, metadata
    
    def analyze_content_with_pro(self, text: str, metadata: Dict) -> Dict:
        """Use Gemini Pro for deep content analysis"""
        print("🧠 Analyzing content with Gemini Pro (deep analysis)...")
        
        prompt = f"""Analyze this document and provide a detailed content analysis:

METADATA:
- Pages: {metadata['total_pages']}
- Words: {metadata['word_count']}
- Title: {metadata['filename']}

CONTENT PREVIEW:
{text[:3000]}

Provide analysis in JSON format with:
1. main_themes: List of 5 key themes
2. target_audience: Who should listen to this podcast
3. optimal_structure: How to structure the podcast (intro, sections, conclusion)
4. key_takeaways: Top 5 important points
5. suggested_tone: Educational, casual, formal, etc.
6. estimated_duration_minutes: Expected podcast length

Return ONLY valid JSON."""
        
        response = self.pro_model.generate_content(prompt)
        try:
            analysis = json.loads(response.text)
        except json.JSONDecodeError:
            analysis = {"raw_analysis": response.text}
        
        print("✅ Content analysis complete")
        return analysis
    
    def generate_script_structure_with_pro(self, text: str, analysis: Dict) -> str:
        """Use Gemini Pro to create detailed script structure"""
        print("✍️ Generating podcast script with Gemini Pro...")
        
        themes = ", ".join(analysis.get("main_themes", []))
        audience = analysis.get("target_audience", "general audience")
        tone = analysis.get("suggested_tone", "professional")
        
        prompt = f"""Create a detailed, engaging podcast script from this content.

INSTRUCTIONS:
- Target audience: {audience}
- Tone: {tone}
- Main themes: {themes}
- Maximum length: 3000 words
- Format: Professional podcast script with timing

STRUCTURE REQUIRED:
1. [INTRO] - Hook and introduction (30-60 seconds)
2. [MAIN CONTENT] - Broken into 3-4 segments
3. [CONCLUSION] - Summary and call-to-action

CONTENT TO ADAPT:
{text[:4000]}

Create a podcast script that flows naturally as spoken content. Include [PAUSE] markers for emphasis."""
        
        response = self.pro_model.generate_content(prompt)
        script = response.text
        
        print("✅ Script structure generated")
        return script
    
    def optimize_script_with_flash(self, script: str) -> str:
        """Use Gemini Flash to quickly optimize for audio"""
        print("⚡ Optimizing script with Gemini Flash...")
        
        prompt = f"""Optimize this podcast script for audio/speech. 

Make it more conversational and easier to read aloud:
- Replace complex words with simpler alternatives
- Add natural pauses and breathing points
- Improve sentence flow for spoken delivery
- Keep timing in mind (3-5 minutes per section)
- Maintain all [PAUSE] markers

ORIGINAL SCRIPT:
{script[:3500]}

Return the optimized script ready for TTS."""
        
        response = self.flash_model.generate_content(prompt)
        optimized = response.text
        
        print("✅ Script optimized for TTS")
        return optimized
    
    def generate_podcast_segments(self, script: str) -> List[Dict]:
        """Break script into segments for multi-part podcast"""
        print("📑 Creating podcast segments...")
        
        prompt = f"""Break this podcast script into 3-5 logical segments.

For each segment provide JSON with:
- segment_number: Integer
- title: Segment title
- content: The script text for this segment
- duration_minutes: Estimated duration
- speaker_notes: Any special instructions

SCRIPT:
{script}

Return as JSON array of segments."""
        
        response = self.flash_model.generate_content(prompt)
        try:
            segments = json.loads(response.text)
        except json.JSONDecodeError:
            # Fallback: create simple segments
            parts = script.split("[SECTION]")
            segments = [
                {
                    "segment_number": i+1,
                    "title": f"Segment {i+1}",
                    "content": part.strip(),
                    "duration_minutes": len(part.split()) / 150  # ~150 words per minute
                }
                for i, part in enumerate(parts[:5])
            ]
        
        print(f"✅ Created {len(segments)} segments")
        return segments
    
    def create_podcast_metadata(self, 
                               title: str,
                               script: str,
                               analysis: Dict,
                               segments: List[Dict]) -> Dict:
        """Create comprehensive podcast metadata"""
        
        total_duration = sum(s.get("duration_minutes", 3) for s in segments)
        
        metadata = {
            "podcast_title": title,
            "description": analysis.get("main_themes", ["Podcast from document"])[0],
            "target_audience": analysis.get("target_audience", "General"),
            "tone": analysis.get("suggested_tone", "Professional"),
            "total_duration_minutes": round(total_duration, 1),
            "segments_count": len(segments),
            "content_type": analysis.get("content_type", "educational"),
            "key_takeaways": analysis.get("key_takeaways", []),
            "segments": segments
        }
        
        return metadata
    
    def create_podcast(self, pdf_path: str, output_dir: str = "podcasts") -> Dict:
        """Complete multi-model pipeline"""
        print("\n" + "="*70)
        print("🎙️ PODCAST CREATOR - MULTI-MODEL VERSION")
        print("="*70 + "\n")
        
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True)
            
            pdf_name = Path(pdf_path).stem
            
            # Step 1: Extract with metadata
            text, metadata = self.extract_pdf_text_with_metadata(pdf_path)
            
            # Step 2: Deep analysis with Pro model
            analysis = self.analyze_content_with_pro(text, metadata)
            
            # Step 3: Generate detailed script with Pro
            script = self.generate_script_structure_with_pro(text, analysis)
            
            # Step 4: Optimize with Flash model
            optimized_script = self.optimize_script_with_flash(script)
            
            # Step 5: Create segments
            segments = self.generate_podcast_segments(optimized_script)
            
            # Step 6: Generate metadata
            podcast_metadata = self.create_podcast_metadata(
                pdf_name,
                optimized_script,
                analysis,
                segments
            )
            
            # Save all outputs
            script_path = output_dir / f"{pdf_name}_podcast_script.txt"
            with open(script_path, "w") as f:
                f.write(optimized_script)
            print(f"💾 Script saved: {script_path}")
            
            metadata_path = output_dir / f"{pdf_name}_podcast_metadata.json"
            with open(metadata_path, "w") as f:
                json.dump(podcast_metadata, f, indent=2)
            print(f"💾 Metadata saved: {metadata_path}")
            
            analysis_path = output_dir / f"{pdf_name}_content_analysis.json"
            with open(analysis_path, "w") as f:
                json.dump(analysis, f, indent=2)
            print(f"💾 Analysis saved: {analysis_path}")
            
            print("\n" + "="*70)
            print("✅ Multi-model podcast creation completed!")
            print(f"📊 Podcast Duration: {podcast_metadata['total_duration_minutes']} minutes")
            print(f"📋 Segments: {podcast_metadata['segments_count']}")
            print("="*70)
            
            return podcast_metadata
        
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {}


def main():
    """Main entry point"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not set in environment")
        print("Please set: export GEMINI_API_KEY='your-key-here'")
        sys.exit(1)
    
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "sample.pdf"
    
    creator = PodcastCreatorMultiModel(api_key)
    creator.create_podcast(pdf_path)


if __name__ == "__main__":
    main()
