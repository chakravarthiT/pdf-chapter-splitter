"""
Gemini AI Integration for Chapter Detection
Uses Google's Gemini API to intelligently detect chapter boundaries
"""

from google import genai
from google.genai import types
import json
import re
import os
import ssl
import certifi
from typing import Optional


def detect_chapters_with_gemini(
    text_content: str,
    total_pages: int,
    api_key: str,
    model_name: str = None
) -> list[dict]:
    """
    Use Gemini AI to detect chapter boundaries from PDF text.
    
    Args:
        text_content: Text extracted from PDF with page markers
        total_pages: Total number of pages in the PDF
        api_key: Gemini API key
        model_name: Gemini model to use
    
    Returns:
        List of dictionaries with 'title', 'start_page', 'end_page'
    """
    try:
        # Configure SSL properly
        os.environ['SSL_CERT_FILE'] = certifi.where()
        os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
        
        # Create client with the new API
        client = genai.Client(api_key=api_key)
        
        # Use fallback model strategy if not specified
        if not model_name:
            model_name = "gemini-pro"  # More widely available
        
        prompt = f"""Analyze this PDF text and identify chapter or section boundaries.
The PDF has {total_pages} total pages.

TEXT CONTENT (with page numbers):
{text_content}

TASK:
1. Identify distinct chapters, sections, or major divisions
2. For each chapter, determine the start and end page numbers
3. If you can't clearly identify chapters, suggest logical divisions based on content

RESPOND WITH ONLY a JSON array in this exact format (no markdown, no explanation):
[
    {{"title": "Chapter/Section Title", "start_page": 1, "end_page": 10}},
    {{"title": "Another Chapter", "start_page": 11, "end_page": 25}}
]

RULES:
- Page numbers must be between 1 and {total_pages}
- Ranges should not overlap
- Ranges should cover all pages from 1 to {total_pages}
- Use descriptive titles based on the content
- Return at least 2 chapters/sections if the document is more than 10 pages
"""
        
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
        except Exception as model_error:
            # If primary model fails, try fallback
            error_msg = str(model_error).lower()
            if "not found" in error_msg or "not supported" in error_msg:
                if model_name != "gemini-pro":
                    try:
                        response = client.models.generate_content(
                            model="gemini-pro",
                            contents=prompt
                        )
                    except Exception:
                        raise Exception(f"No supported Gemini models available. Error: {str(model_error)}")
                else:
                    raise Exception(f"Gemini model not available: {str(model_error)}")
            else:
                raise
        
        response_text = response.text.strip()
        
        # Try to extract JSON from response
        chapters = _parse_ai_response(response_text, total_pages)
        
        return chapters
        
    except Exception as e:
        raise Exception(f"Gemini API Error: {str(e)}")


def _parse_ai_response(response_text: str, total_pages: int) -> list[dict]:
    """Parse and validate AI response"""
    
    # Try to extract JSON from the response
    # Sometimes AI wraps it in markdown code blocks
    json_match = re.search(r'\[[\s\S]*\]', response_text)
    
    if not json_match:
        raise ValueError("Could not find JSON array in AI response")
    
    try:
        chapters = json.loads(json_match.group())
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in AI response: {e}")
    
    # Validate and clean the chapters
    validated = []
    for ch in chapters:
        if not isinstance(ch, dict):
            continue
            
        title = str(ch.get('title', 'Untitled'))
        start = int(ch.get('start_page', 1))
        end = int(ch.get('end_page', total_pages))
        
        # Ensure valid range
        start = max(1, min(start, total_pages))
        end = max(start, min(end, total_pages))
        
        validated.append({
            'title': title,
            'start_page': start,
            'end_page': end
        })
    
    # Sort by start page
    validated.sort(key=lambda x: x['start_page'])
    
    # Fill gaps and fix overlaps
    validated = _fix_ranges(validated, total_pages)
    
    return validated


def _fix_ranges(chapters: list[dict], total_pages: int) -> list[dict]:
    """Fix gaps and overlaps in chapter ranges"""
    if not chapters:
        return [{'title': 'Full Document', 'start_page': 1, 'end_page': total_pages}]
    
    fixed = []
    
    for i, ch in enumerate(chapters):
        start = ch['start_page']
        end = ch['end_page']
        
        # Adjust start if there's a gap from previous
        if fixed:
            prev_end = fixed[-1]['end_page']
            if start > prev_end + 1:
                # There's a gap - extend previous chapter or adjust this one
                start = prev_end + 1
            elif start <= prev_end:
                # Overlap - adjust this chapter's start
                start = prev_end + 1
        else:
            # First chapter should start at 1
            if start > 1:
                start = 1
        
        # Ensure end is at least start
        end = max(start, end)
        
        if start <= total_pages:
            fixed.append({
                'title': ch['title'],
                'start_page': start,
                'end_page': min(end, total_pages)
            })
    
    # Ensure last chapter goes to the end
    if fixed and fixed[-1]['end_page'] < total_pages:
        fixed[-1]['end_page'] = total_pages
    
    return fixed


def validate_api_key(api_key: str) -> tuple[bool, str]:
    """
    Validate if the Gemini API key is working.
    
    Returns:
        (is_valid, message)
    """
    if not api_key or len(api_key) < 10:
        return False, "API key is too short"
    
    try:
        # Configure SSL properly
        os.environ['SSL_CERT_FILE'] = certifi.where()
        os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
        
        client = genai.Client(api_key=api_key)
        
        # Try multiple models to find one that works
        models_to_try = ["gemini-pro", "gemini-2.0-flash", "gemini-1.5-pro"]
        
        for model in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents="Say 'OK' if you can read this."
                )
                if response and response.text:
                    return True, f"API key is valid (using {model})"
            except Exception as e:
                error_str = str(e).lower()
                if "not found" in error_str or "not supported" in error_str:
                    continue  # Try next model
                else:
                    raise  # Re-raise other errors
        
        return False, "API key validation failed - no supported models available"
            
    except Exception as e:
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
            return False, "Invalid API key"
        elif "quota" in error_msg.lower():
            return False, "API quota exceeded"
        else:
            return False, f"API error: {error_msg}"
