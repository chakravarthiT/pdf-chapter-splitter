"""
Utility functions for PDF Splitter
"""

import zipfile
import io
from datetime import datetime


def create_zip(files: list[tuple[str, bytes]], zip_name: str = None) -> bytes:
    """
    Create a ZIP file from a list of files.
    
    Args:
        files: List of (filename, file_bytes) tuples
        zip_name: Optional name for the zip (not used in output, just for metadata)
    
    Returns:
        ZIP file as bytes
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename, file_bytes in files:
            zf.writestr(filename, file_bytes)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def generate_output_filename(original_name: str) -> str:
    """Generate output ZIP filename based on original PDF name"""
    # Remove .pdf extension
    base_name = original_name.rsplit('.', 1)[0] if '.' in original_name else original_name
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    return f"{base_name}_split_{timestamp}.zip"


def validate_ranges(ranges: list[tuple[int, int, str]], total_pages: int) -> tuple[bool, str]:
    """
    Validate that ranges are valid and cover the document properly.
    
    Returns:
        (is_valid, error_message)
    """
    if not ranges:
        return False, "No ranges specified"
    
    # Check each range
    for start, end, name in ranges:
        if start < 1:
            return False, f"Range '{name}' has invalid start page: {start}"
        if end > total_pages:
            return False, f"Range '{name}' exceeds total pages: {end} > {total_pages}"
        if start > end:
            return False, f"Range '{name}' has start > end: {start} > {end}"
    
    # Sort by start page
    sorted_ranges = sorted(ranges, key=lambda x: x[0])
    
    # Check for overlaps
    for i in range(len(sorted_ranges) - 1):
        current_end = sorted_ranges[i][1]
        next_start = sorted_ranges[i + 1][0]
        
        if current_end >= next_start:
            return False, f"Ranges overlap: '{sorted_ranges[i][2]}' ends at {current_end}, '{sorted_ranges[i + 1][2]}' starts at {next_start}"
    
    return True, "Valid"


def suggest_equal_splits(total_pages: int, num_parts: int) -> list[tuple[int, int, str]]:
    """
    Suggest equal splits for a document.
    
    Args:
        total_pages: Total number of pages
        num_parts: Number of parts to split into
    
    Returns:
        List of (start, end, name) tuples
    """
    if num_parts <= 0:
        num_parts = 1
    if num_parts > total_pages:
        num_parts = total_pages
    
    pages_per_part = total_pages // num_parts
    remainder = total_pages % num_parts
    
    ranges = []
    current_page = 1
    
    for i in range(num_parts):
        # Distribute remainder across first few parts
        extra = 1 if i < remainder else 0
        part_pages = pages_per_part + extra
        
        end_page = current_page + part_pages - 1
        ranges.append((current_page, end_page, f"Part {i + 1}"))
        
        current_page = end_page + 1
    
    return ranges


def fill_missing_pages(chapters: list, total_pages: int) -> list:
    """Fill gaps in chapter ranges by adding 'Uncovered Pages' chapters.
    
    Args:
        chapters: List of Chapter objects or (start, end, name) tuples
        total_pages: Total number of pages in document
    
    Returns:
        List with gaps filled
    """
    from src.pdf_processor import Chapter
    
    if not chapters:
        return [(1, total_pages, "Full Document")]
    
    # Convert to list of tuples if needed
    ranges = []
    for ch in chapters:
        if isinstance(ch, Chapter):
            ranges.append((ch.start_page, ch.end_page, ch.title))
        else:
            ranges.append(ch)
    
    # Sort by start page
    ranges.sort(key=lambda x: x[0])
    
    filled_ranges = []
    current_page = 1
    
    for start, end, title in ranges:
        # If there's a gap before this chapter, fill it
        if start > current_page:
            gap_title = f"Uncovered Pages {current_page}-{start-1}"
            filled_ranges.append((current_page, start - 1, gap_title))
        
        # Add the current chapter
        filled_ranges.append((start, end, title))
        current_page = end + 1
    
    # Fill any remaining pages at the end
    if current_page <= total_pages:
        gap_title = f"Uncovered Pages {current_page}-{total_pages}"
        filled_ranges.append((current_page, total_pages, gap_title))
    
    return filled_ranges
