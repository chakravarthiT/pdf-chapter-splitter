# Changes Summary - PDF Splitter Improvements

## Date: February 4, 2026

## Issues Fixed

### 1. ✅ Chapter Editor Limitations
**Problem:** Could only add chapters at the end, not in the middle.

**Solution:**
- Improved data editor configuration with `num_rows="dynamic"`
- Added clear instructions with 💡 tip showing users can use the + button
- Added `hide_index=True` for cleaner interface
- Added `#` column to show chapter order
- Made fields required with better validation

**Changes:**
- Added helpful tip: "Use the + button to add rows anywhere in the table"
- Better column configuration with width and help text
- Improved Apply Changes button with validation

### 2. ✅ Auto-Numbering for Downloaded Files
**Problem:** Downloaded PDF files had no numbering, making it hard to track order.

**Solution:**
- Added automatic zero-padded numbering prefix (01_, 02_, 03_, etc.)
- Number of digits adjusts based on total chapters (e.g., 001_ for 100+ chapters)
- Applied in `split_by_chapters()` method

**Example:**
```
Before: Chapter 1.pdf, Introduction.pdf
After:  01_Chapter 1.pdf, 02_Introduction.pdf
```

**Changes:**
- Modified `src/pdf_processor.py` - `split_by_chapters()` now adds numbering prefix
- Updated preview section to show how files will be numbered
- Files maintain order when downloaded and extracted

### 3. ✅ SSL Certificate Error Fix
**Problem:** Gemini API failing with SSL certificate verification error on macOS:
```
SSL_ERROR_SSL: error:1000007d:SSL routines:OPENSSL_internal:CERTIFICATE_VERIFY_FAILED
```

**Solution:**
- Changed from gRPC transport to REST transport
- Added environment variables for gRPC configuration
- Updated both API detection and validation functions

**Changes:**
- Added `transport='rest'` parameter to `genai.configure()`
- Set environment variables:
  - `GRPC_ENABLE_FORK_SUPPORT=0`
  - `GRPC_POLL_STRATEGY=poll`
- Applied to both `detect_chapters_with_gemini()` and `validate_api_key()`

## Additional Improvements

### UI/UX Enhancements
- Added direct link to Google AI Studio in sidebar for API key
- Updated help section with new features
- Improved preview section to show numbering prefix
- Better error handling and validation messages
- Clearer instructions throughout the app

### Files Modified
1. `/src/gemini_detector.py` - SSL fix with REST transport
2. `/src/pdf_processor.py` - Auto-numbering in split_by_chapters()
3. `/app.py` - Improved editor UX and numbering preview

## Testing Notes

### To Test SSL Fix:
1. Get a Gemini API key from https://makersuite.google.com/app/apikey
2. Enter it in the sidebar
3. Click "Validate API Key" - should succeed without SSL errors
4. Upload a PDF and use "AI Detection" tab - should work without errors

### To Test Chapter Editor:
1. Upload a PDF with detected chapters
2. In the data editor, click the + button on any row
3. Should be able to insert new chapters anywhere
4. Click "Apply Changes" to save

### To Test Auto-Numbering:
1. Set up some chapters (any method)
2. View the preview - should see numbers like "01_"
3. Click "Split PDF" then download ZIP
4. Extract and verify files are named: 01_Title.pdf, 02_Title.pdf, etc.

## Known Issues

⚠️ **FutureWarning**: The `google.generativeai` package is deprecated. Future versions should migrate to `google.genai` package. This doesn't affect functionality currently.

## Next Steps (Optional Enhancements)

1. Add option to choose numbering style (numbers vs letters: a, b, c)
2. Add drag-and-drop reordering in the table
3. Migrate to new `google.genai` package when stable
4. Add batch processing for multiple PDFs
5. Add password-protected PDF support
