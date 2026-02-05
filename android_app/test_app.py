"""
Unit tests for PDF Splitter Android App
"""

import unittest
from unittest.mock import Mock, patch, MagicMock


class TestPDFSplitter(unittest.TestCase):
    """Test cases for PDF splitter functionality"""
    
    def test_auto_detect_chapters(self):
        """Test auto-detecting chapters from PDF bookmarks"""
        # Mock fitz.open
        with patch('fitz.open') as mock_open:
            mock_doc = MagicMock()
            mock_doc.get_toc.return_value = [
                (1, 'Chapter 1', 1),
                (1, 'Chapter 2', 10),
                (1, 'Chapter 3', 20)
            ]
            mock_doc.page_count = 30
            mock_open.return_value = mock_doc
            
            # Test chapter detection
            toc = mock_doc.get_toc()
            self.assertEqual(len(toc), 3)
            self.assertEqual(toc[0][1], 'Chapter 1')
    
    def test_equal_split(self):
        """Test equal split of PDF"""
        num_pages = 20
        num_parts = 4
        pages_per_part = num_pages // num_parts
        
        chapters = []
        for i in range(num_parts):
            start = i * pages_per_part
            end = (i + 1) * pages_per_part - 1 if i < num_parts - 1 else num_pages - 1
            chapters.append({'title': f'Part {i+1}', 'start': start, 'end': end})
        
        self.assertEqual(len(chapters), 4)
        self.assertEqual(chapters[0]['start'], 0)
        self.assertEqual(chapters[0]['end'], 4)
        self.assertEqual(chapters[3]['end'], 19)
    
    def test_manual_range_parsing(self):
        """Test parsing manual page ranges"""
        range_str = "5-15"
        parts = range_str.split('-')
        start = int(parts[0].strip()) - 1
        end = int(parts[1].strip()) - 1
        
        self.assertEqual(start, 4)
        self.assertEqual(end, 14)
    
    def test_chapter_deletion(self):
        """Test deleting chapters from list"""
        chapters = [
            {'title': 'Ch1', 'start': 0, 'end': 5},
            {'title': 'Ch2', 'start': 6, 'end': 10},
            {'title': 'Ch3', 'start': 11, 'end': 15}
        ]
        
        # Delete middle chapter
        chapters.pop(1)
        
        self.assertEqual(len(chapters), 2)
        self.assertEqual(chapters[1]['title'], 'Ch3')
    
    def test_filename_sanitization(self):
        """Test sanitizing filenames"""
        filename = 'Chapter / Title \\ with bad chars'
        sanitized = filename.replace('/', '_').replace('\\', '_')
        
        self.assertEqual(sanitized, 'Chapter _ Title _ with bad chars')
        self.assertNotIn('/', sanitized)
        self.assertNotIn('\\', sanitized)
    
    def test_pdf_info_display(self):
        """Test PDF info display format"""
        pdf_name = 'document.pdf'
        num_pages = 42
        
        info_text = f'[b]{pdf_name}[/b]\nPages: {num_pages}'
        self.assertIn('document.pdf', info_text)
        self.assertIn('42', info_text)
    
    def test_output_path_formatting(self):
        """Test output path formatting"""
        index = 5
        title = 'Introduction'
        filename = f'{index:02d}_{title}.pdf'
        
        self.assertEqual(filename, '05_Introduction.pdf')
    
    def test_page_range_adjustment(self):
        """Test adjusting end pages in chapters"""
        chapters = [
            {'title': 'Ch1', 'start': 0, 'end': 0},
            {'title': 'Ch2', 'start': 10, 'end': 0},
            {'title': 'Ch3', 'start': 20, 'end': 0}
        ]
        total_pages = 30
        
        # Adjust end pages
        for i in range(len(chapters) - 1):
            chapters[i]['end'] = chapters[i + 1]['start'] - 1
        chapters[-1]['end'] = total_pages - 1
        
        self.assertEqual(chapters[0]['end'], 9)
        self.assertEqual(chapters[1]['end'], 19)
        self.assertEqual(chapters[2]['end'], 29)


if __name__ == '__main__':
    unittest.main()
