# Split PDF with Chapters 📄✂️

**Dual-platform PDF splitting tool** with intelligent chapter detection. Available as both a **web app** (Streamlit) and **mobile app** (Android/Kivy).

## 🚀 Quick Start

### Web App (Streamlit)
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Mobile App (Android)
Download from [Releases](../../releases) or see [android_app/README.md](android_app/README.md) for building instructions.

## ✨ Features

### Both Apps Support
- ✅ Auto-detect chapters from PDF bookmarks/TOC
- ✅ Manual chapter editing (title, page range)
- ✅ Add/delete chapters
- ✅ Fill gaps between chapters  
- ✅ Quick equal split (2-20 parts)
- ✅ Manual page ranges (pre-populated with current chapters!)
- ✅ Auto-numbered output files (01_, 02_, etc.)
- ✅ Color-coded status messages

### Web App Only
- ✅ Google Gemini AI chapter detection
- ✅ ZIP download of all splits
- ✅ Browser-based interface

### Mobile App Only  
- ✅ Professional touch-optimized UI (16-color theme)
- ✅ Offline operation (no internet needed)
- ✅ File system integration
- ✅ Native Android performance

## Installation

### Web App Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Web App Setup

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

### Mobile App Installation

See [android_app/README.md](android_app/README.md) for:
- Android device requirements
- Installation from GitHub Releases
- Building APK locally

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
├── requirements.txt            # Python dependencies (web app)
├── .github/
│   └── workflows/
│       └── build-apk.yml       # GitHub Actions APK builder
├── android_app/                # Mobile app (Kivy + PyMuPDF)
│   ├── main.py                 # Android/Kivy application
│   ├── buildozer.spec          # Android build configuration
│   ├── requirements.txt        # Mobile app dependencies
│   ├── test_app.py            # Unit tests (8+ tests)
│   ├── README.md              # Mobile app documentation
│   ├── BUILD_GUIDE.md         # APK build instructions
│   ├── TROUBLESHOOTING.md     # Common issues and solutions
│   └── bin/
│       └── pdfsplitter-1.0.0-debug.apk  # Compiled APK
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

## CI/CD Pipeline

**GitHub Actions** automatically builds APK for each commit:

1. Push to `main` or `develop` branch
2. GitHub Actions triggers build workflow
3. APK available as artifact (90-day retention)
4. GitHub Release created with APK attached
5. APK committed back to repository

### Build Locations
- **Artifacts**: Actions tab → Latest run → `apk-build` artifact
- **Releases**: Repository Releases page
- **Repository**: `android_app/bin/pdfsplitter-1.0.0-debug.apk`

See `.github/workflows/build-apk.yml` for configuration details.

## Building APK Locally

### Option 1: Docker (Recommended)
```bash
cd android_app
docker build -t pdfsplitter-builder -f Dockerfile .
docker run --rm -v $(pwd):/workspace pdfsplitter-builder
```

### Option 2: Direct Buildozer
```bash
cd android_app
pip install buildozer cython kivy pymupdf
buildozer android debug
```

See [android_app/BUILD_GUIDE.md](android_app/BUILD_GUIDE.md) for detailed instructions.

## Technologies Used

### Web App
- **[Streamlit](https://streamlit.io/)** - Web UI framework
- **[PyMuPDF](https://pymupdf.readthedocs.io/)** - PDF processing
- **[Google Generative AI](https://ai.google.dev/)** - Gemini API for AI detection

### Mobile App  
- **[Kivy](https://kivy.org/)** - Touch-optimized UI framework
- **[PyMuPDF](https://pymupdf.readthedocs.io/)** - PDF processing
- **[Buildozer](https://buildozer.readthedocs.io/)** - APK compilation
- **Python 3.11** - Application logic
- **Android API 29** - Target platform

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
