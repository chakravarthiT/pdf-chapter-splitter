# Split PDF with Chapters 📄✂️

**PDF splitting tool** with intelligent chapter detection powered by a modern **web app** (Streamlit).

## 🚀 Quick Start

```bash
uv sync
uv run streamlit run app.py
```

## ✨ Features

- ✅ Auto-detect chapters from PDF bookmarks/TOC
- ✅ Manual chapter editing (title, page range)
- ✅ Add/delete chapters
- ✅ Fill gaps between chapters  
- ✅ Quick equal split (2-20 parts)
- ✅ Manual page ranges (pre-populated with current chapters!)
- ✅ Auto-numbered output files (01_, 02_, etc.)
- ✅ Color-coded status messages
- ✅ Google Gemini AI chapter detection
- ✅ ZIP download of all splits
- ✅ Browser-based interface

## Installation

### Prerequisites
- Python 3.9 or higher
- [uv](https://docs.astral.sh/uv/) (fast Python package installer)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd split-pdf-with-chapters
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Run the application**
   ```bash
   uv run streamlit run app.py
   ```

4. **Open in browser**
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
├── app.py                      # Main Streamlit web application
├── requirements.txt            # Python dependencies
├── src/
│   ├── __init__.py
│   ├── pdf_processor.py        # PDF reading, splitting, chapter detection
│   ├── gemini_detector.py      # AI-based chapter detection
│   └── utils.py                # Helper functions
├── docs/
│   └── DESIGN.md               # Design document
├── .streamlit/
│   └── config.toml             # Streamlit configuration
└── README.md                   # This file
```

## Technologies Used

- **[Streamlit](https://streamlit.io/)** - Web UI framework
- **[PyMuPDF](https://pymupdf.readthedocs.io/)** - PDF processing
- **[Google Generative AI](https://ai.google.dev/)** - Gemini API for AI detection
- **[uv](https://docs.astral.sh/uv/)** - Fast Python package manager

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
