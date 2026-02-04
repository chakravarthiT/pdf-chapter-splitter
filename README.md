# PDF Splitter with Chapter Detection

✂️ A web application to split PDFs into multiple files based on chapters or custom page ranges.

## Features

- **📤 PDF Upload** - Drag & drop or click to upload
- **📚 Auto Chapter Detection** - Extracts chapters from PDF bookmarks/TOC
- **🔍 Smart Text Analysis** - Detects chapters by analyzing text patterns (even without bookmarks)
- **🤖 AI-Powered Detection** - Uses Google Gemini to intelligently identify chapter boundaries
- **✏️ Editable Ranges** - Edit detected chapters or input custom page ranges
- **📦 ZIP Download** - Download all split files as a single ZIP

## Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd split-pdf-with-chapters
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   .\venv\Scripts\activate   # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open in browser**
   The app will automatically open at `http://localhost:8501`

## Usage

### Basic Usage

1. **Upload a PDF** - Click or drag a PDF file to the upload area
2. **View detected chapters** - The app automatically detects chapters from:
   - PDF bookmarks/Table of Contents
   - Text pattern analysis (Chapter 1, Section 2, etc.)
3. **Edit if needed** - Modify chapter titles, start/end pages
4. **Split & Download** - Click "Split PDF" and download the ZIP file

### Manual Range Input

Use the "Manual Input" tab to enter custom ranges:
- Simple format: `1-10, 11-20, 21-30`
- With names: `1-10:Introduction, 11-50:Main Content, 51-100:Appendix`

### AI Detection (Optional)

1. Get a free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Enter the API key in the sidebar
3. Use the "AI Detection" tab to auto-detect chapters

## Project Structure

```
split-pdf-with-chapters/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── src/
│   ├── __init__.py
│   ├── pdf_processor.py    # PDF reading, splitting, chapter detection
│   ├── gemini_detector.py  # AI-based chapter detection
│   └── utils.py            # Helper functions
├── docs/
│   └── DESIGN.md           # Design document
├── .streamlit/
│   └── config.toml         # Streamlit configuration
└── README.md               # This file
```

## Technologies Used

- **[Streamlit](https://streamlit.io/)** - Web UI framework
- **[PyMuPDF](https://pymupdf.readthedocs.io/)** - PDF processing (superior TOC extraction and text analysis)
- **[Google Generative AI](https://ai.google.dev/)** - Gemini API for AI detection

## Why PyMuPDF?

We chose PyMuPDF (fitz) over other libraries because:
1. **Better TOC/bookmark extraction** - More reliable than pypdf
2. **Text analysis with font info** - Can detect headings by font size
3. **Faster processing** - Better performance for large PDFs
4. **Rich text extraction** - Better for AI analysis

## Deployment

### Streamlit Cloud (Free)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Deploy!

### Other Options
- Heroku
- Railway
- Google Cloud Run
- AWS Elastic Beanstalk

## License

MIT License - feel free to use and modify!

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
