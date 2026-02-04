"""
PDF Processor Module
Handles PDF reading, splitting, and chapter detection using PyMuPDF (fitz)

PyMuPDF is chosen over pypdf because:
1. Better TOC/bookmark extraction
2. Can detect chapters by font size analysis (not just metadata)
3. Faster processing
4. Better text extraction for AI analysis
"""

import fitz  # PyMuPDF
import io
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class Chapter:
    """Represents a chapter/section in the PDF"""
    title: str
    start_page: int  # 1-indexed
    end_page: int    # 1-indexed, inclusive
    level: int = 1   # Nesting level (1 = top level)
    
    def __str__(self):
        return f"{self.title} (Pages {self.start_page}-{self.end_page})"


@dataclass
class PDFInfo:
    """Contains information about a PDF file"""
    filename: str
    total_pages: int
    file_size_mb: float
    has_toc: bool
    chapters: list[Chapter]
    metadata: dict


class PDFProcessor:
    """Main class for PDF processing operations"""
    
    def __init__(self, pdf_bytes: bytes, filename: str = "document.pdf"):
        """Initialize with PDF bytes"""
        self.pdf_bytes = pdf_bytes
        self.filename = filename
        self.doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
    def get_toc_depth(self) -> int:
        """Get the maximum depth of the TOC"""
        toc = self.doc.get_toc()
        if not toc:
            return 0
        levels = [item[0] for item in toc]
        min_level = min(levels)
        max_level = max(levels)
        return max_level - min_level + 1
    
    def get_info(self, toc_depth: int = 2) -> PDFInfo:
        """Extract PDF information including detected chapters
        
        Args:
            toc_depth: Maximum depth for TOC extraction (1 = top level only, 2 = two levels, etc.)
        """
        toc = self.doc.get_toc()  # Returns list of [level, title, page_num]
        chapters = self._toc_to_chapters(toc, toc_depth) if toc else []
        
        # If no TOC, try to detect chapters by analyzing text
        if not chapters:
            chapters = self._detect_chapters_by_text()
        
        return PDFInfo(
            filename=self.filename,
            total_pages=len(self.doc),
            file_size_mb=len(self.pdf_bytes) / (1024 * 1024),
            has_toc=bool(toc),
            chapters=chapters,
            metadata=dict(self.doc.metadata) if self.doc.metadata else {}
        )
    
    def _toc_to_chapters(self, toc: list, max_depth: int = 2) -> list[Chapter]:
        """Convert PDF TOC to Chapter objects
        
        Args:
            toc: Table of contents from PDF
            max_depth: Maximum depth level to include (1 = top level only, 2 = include level 1 and 2, etc.)
        """
        if not toc:
            return []
        
        chapters = []
        total_pages = len(self.doc)
        
        # Get min level in TOC
        levels = [item[0] for item in toc]
        min_level = min(levels) if levels else 1
        
        # Filter entries up to max_depth from min_level
        max_level = min_level + max_depth - 1
        filtered_entries = [(i, item) for i, item in enumerate(toc) 
                           if min_level <= item[0] <= max_level]
        
        # Build a list with hasChildren flag
        entries_with_meta = []
        for idx, (toc_idx, entry) in enumerate(filtered_entries):
            level, title, start_page = entry
            
            # Check if this entry has children (next entry is deeper level)
            has_children = False
            if idx + 1 < len(filtered_entries):
                next_level = filtered_entries[idx + 1][1][0]
                if next_level > level:
                    has_children = True
            
            entries_with_meta.append({
                'level': level,
                'title': title,
                'start_page': start_page,
                'has_children': has_children,
                'original_idx': idx
            })
        
        # Filter to only leaf nodes (no children)
        leaf_entries = [e for e in entries_with_meta if not e['has_children']]
        
        # Now create chapters from leaf nodes only
        for idx, entry in enumerate(leaf_entries):
            level = entry['level']
            title = entry['title']
            start_page = entry['start_page']
            
            # Find end page - simply use the next leaf entry's start page - 1
            end_page = total_pages
            if idx + 1 < len(leaf_entries):
                end_page = leaf_entries[idx + 1]['start_page'] - 1
            
            # Ensure valid range
            if start_page > 0 and end_page >= start_page:
                # Add indentation to title based on level for visual hierarchy
                indent = "  " * (level - min_level)
                chapters.append(Chapter(
                    title=indent + title.strip(),
                    start_page=start_page,
                    end_page=end_page,
                    level=level
                ))
        
        return chapters
    
    def _detect_chapters_by_text(self) -> list[Chapter]:
        """
        Detect chapters by analyzing text patterns and font sizes.
        This works even when PDF has no bookmarks/TOC.
        """
        chapters = []
        total_pages = len(self.doc)
        
        # Common chapter patterns
        chapter_patterns = [
            r'^chapter\s+\d+',           # "Chapter 1", "Chapter 10"
            r'^chapter\s+[ivxlc]+',       # "Chapter I", "Chapter IV"
            r'^\d+\.\s+\w+',              # "1. Introduction"
            r'^part\s+\d+',               # "Part 1"
            r'^section\s+\d+',            # "Section 1"
            r'^unit\s+\d+',               # "Unit 1"
            r'^module\s+\d+',             # "Module 1"
        ]
        
        potential_chapters = []
        
        for page_num in range(total_pages):
            page = self.doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            # Look at the first few text blocks on each page
            for block in blocks[:5]:  # Check first 5 blocks
                if "lines" not in block:
                    continue
                    
                for line in block["lines"]:
                    text = ""
                    max_font_size = 0
                    
                    for span in line["spans"]:
                        text += span["text"]
                        max_font_size = max(max_font_size, span["size"])
                    
                    text = text.strip()
                    if not text or len(text) < 3:
                        continue
                    
                    # Check if this looks like a chapter heading
                    is_chapter = False
                    for pattern in chapter_patterns:
                        if re.match(pattern, text.lower()):
                            is_chapter = True
                            break
                    
                    # Also consider large font text at the start of a page
                    if max_font_size >= 14 and len(text) < 100:
                        # Likely a heading
                        is_chapter = True
                    
                    if is_chapter:
                        potential_chapters.append({
                            'title': text[:80],  # Truncate long titles
                            'page': page_num + 1,  # 1-indexed
                            'font_size': max_font_size
                        })
                        break  # Only first match per page
                
                if potential_chapters and potential_chapters[-1]['page'] == page_num + 1:
                    break
        
        # Convert to Chapter objects
        for idx, ch in enumerate(potential_chapters):
            if idx + 1 < len(potential_chapters):
                end_page = potential_chapters[idx + 1]['page'] - 1
            else:
                end_page = total_pages
            
            if end_page >= ch['page']:
                chapters.append(Chapter(
                    title=ch['title'],
                    start_page=ch['page'],
                    end_page=end_page,
                    level=1
                ))
        
        return chapters
    
    def split_by_ranges(self, ranges: list[tuple[int, int, str]]) -> list[tuple[str, bytes]]:
        """
        Split PDF by page ranges.
        
        Args:
            ranges: List of (start_page, end_page, filename) tuples
                   Pages are 1-indexed, end is inclusive
        
        Returns:
            List of (filename, pdf_bytes) tuples
        """
        result = []
        
        for start, end, name in ranges:
            # Create new PDF with selected pages
            new_doc = fitz.open()
            
            # PyMuPDF uses 0-indexed pages
            new_doc.insert_pdf(
                self.doc,
                from_page=start - 1,
                to_page=end - 1
            )
            
            # Get bytes
            pdf_bytes = new_doc.write()
            new_doc.close()
            
            # Sanitize filename
            safe_name = self._sanitize_filename(name)
            if not safe_name.endswith('.pdf'):
                safe_name += '.pdf'
            
            result.append((safe_name, pdf_bytes))
        
        return result
    
    def split_by_chapters(self, chapters: list[Chapter], add_numbering: bool = True) -> list[tuple[str, bytes]]:
        """Split PDF by chapter objects with optional numbering prefix"""
        ranges = []
        for idx, ch in enumerate(chapters, 1):
            # Add numbering prefix to maintain order
            if add_numbering:
                # Use zero-padded numbers for proper sorting (01, 02, 03...)
                num_digits = len(str(len(chapters)))
                prefix = f"{idx:0{num_digits}d}_"
                title = prefix + ch.title
            else:
                title = ch.title
            ranges.append((ch.start_page, ch.end_page, title))
        return self.split_by_ranges(ranges)
    
    def get_page_text(self, page_num: int) -> str:
        """Get text content of a specific page (1-indexed)"""
        if 1 <= page_num <= len(self.doc):
            return self.doc[page_num - 1].get_text()
        return ""
    
    def get_text_for_ai(self, max_pages: int = 20) -> str:
        """
        Extract text suitable for AI analysis.
        Gets first lines from each page to help identify chapter boundaries.
        """
        result = []
        pages_to_check = min(len(self.doc), max_pages * 3)  # Check more pages, sample them
        
        # Sample pages evenly across the document
        step = max(1, len(self.doc) // max_pages)
        
        for i in range(0, len(self.doc), step):
            if len(result) >= max_pages:
                break
                
            page = self.doc[i]
            text = page.get_text()[:500]  # First 500 chars
            
            # Clean up the text
            text = ' '.join(text.split())
            if text:
                result.append(f"[Page {i + 1}]: {text}")
        
        return "\n\n".join(result)
    
    def _sanitize_filename(self, name: str) -> str:
        """Remove invalid characters from filename"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        
        # Limit length
        name = name[:100]
        
        # Remove leading/trailing spaces and dots
        name = name.strip('. ')
        
        return name if name else "chapter"
    
    def close(self):
        """Close the PDF document"""
        self.doc.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def parse_range_string(range_str: str, total_pages: int) -> list[tuple[int, int, str]]:
    """
    Parse a range string into list of (start, end, name) tuples.
    
    Examples:
        "1-10, 11-20, 21-30" -> [(1, 10, "Part 1"), (11, 20, "Part 2"), (21, 30, "Part 3")]
        "1-10:Intro, 11-50:Main" -> [(1, 10, "Intro"), (11, 50, "Main")]
    """
    ranges = []
    parts = range_str.split(',')
    
    for i, part in enumerate(parts):
        part = part.strip()
        if not part:
            continue
        
        # Check if custom name is provided (format: "1-10:Name")
        if ':' in part:
            range_part, name = part.split(':', 1)
            name = name.strip()
        else:
            range_part = part
            name = f"Part {i + 1}"
        
        # Parse the range
        if '-' in range_part:
            try:
                start, end = map(int, range_part.split('-'))
                # Validate
                start = max(1, min(start, total_pages))
                end = max(start, min(end, total_pages))
                ranges.append((start, end, name))
            except ValueError:
                continue
    
    return ranges
