# PDF Splitter - Android/Kivy Mobile App

A native Android application for splitting PDF files by chapters or custom page ranges. Built with Python and Kivy framework for optimal mobile experience.

## 📋 Features

### Core Functionality
- ✅ **Auto-Detect Chapters**: Extract chapters from PDF bookmarks/TOC
- ✅ **Manual Chapter Editing**: Add, edit, or delete chapters
- ✅ **Fill Gaps**: Automatically fill gaps between detected chapters
- ✅ **Table of Contents Support**: Handle multi-level TOC (1-10 levels)
- ✅ **Equal Split**: Quickly split PDF into equal parts (2-20 divisions)
- ✅ **Manual Page Ranges**: Specify exact page ranges with pre-populated defaults
- ✅ **Auto-Numbered Output**: Files automatically numbered 01_, 02_, etc.
- ✅ **Color-Coded Status**: Visual feedback for all operations

### Mobile-Specific Features
- 📱 **Touch-Optimized UI**: Professional 16-color theme
- 🔌 **Offline Support**: Works completely without internet
- 📂 **File System Integration**: Direct access to device storage
- ⚡ **Native Performance**: Optimized for mobile devices
- 🎨 **Responsive Layout**: Adapts to any screen size

## 🚀 Quick Start

### Prerequisites
- Android 5.1+ (API 21+) - Recommended: Android 9+ (API 29+)
- 50MB free storage for APK
- 100MB free storage for split PDFs

### Installation

**Option 1: GitHub (Easiest)**
1. Go to repository [Releases](../../releases)
2. Download latest `pdfsplitter-1.0.0-debug.apk`
3. Transfer to Android device
4. Open APK → Install → Grant Permissions

**Option 2: From Repository**
```bash
# Clone repository
git clone https://github.com/[owner]/split-pdf-with-chapters.git
cd android_app

# Build locally (see BUILD_GUIDE.md)
buildozer android debug

# Install on device
adb install bin/pdfsplitter-1.0.0-debug.apk
```

### Permissions
Grant the following permissions when prompted:
- **Storage**: Access PDF files and save splits
- **Internet**: For future AI chapter detection (optional)

## 📖 Usage Guide

### 1. Select PDF
1. Tap **"Select PDF File"** button
2. Browse device storage
3. Choose PDF to split

### 2. Configure Chapters

#### Auto-Detect (Recommended)
- Tap **"Auto Detect"** to extract from PDF bookmarks
- App automatically adjusts page ranges

#### Equal Split
- Tap **"Equal Split"** 
- Enter number of parts (2-20)
- PDF splits into equal sections

#### Manual Ranges
- Tap **"Manual Ranges"**
- Enter chapter name and page range (e.g., "1-10")
- Add multiple chapters

### 3. Review & Edit
- View all chapters in the list
- Tap **"Delete"** to remove chapter
- Scroll to see all chapters

### 4. Split PDF
- Review configuration
- Tap **"Split PDF"** (green button)
- Wait for completion
- Files saved to: `/sdcard/DCIM/PDFSplitter/`

## 📁 Output Format

**Default Output Location:**
```
/sdcard/DCIM/PDFSplitter/
├── 01_Introduction.pdf
├── 02_Chapter_1.pdf
├── 03_Chapter_2.pdf
└── 04_Appendix.pdf
```

**File Naming:**
- Format: `{number:02d}_{title}.pdf`
- Numbers: 01, 02, 03... (sequential)
- Titles: Sanitized (special characters removed)

## 🛠️ Building APK

### Option 1: GitHub Actions (Easiest - Recommended)
APK builds automatically when pushing to repository:
```bash
git push origin main
# → GitHub Actions builds APK automatically
# → Download from Releases or Artifacts tab
```

### Option 2: Docker Build
```bash
cd android_app
docker build -t pdfsplitter-builder -f Dockerfile .
docker run --rm -v $(pwd):/workspace pdfsplitter-builder
```

### Option 3: Direct Buildozer
```bash
cd android_app
pip install buildozer cython kivy pymupdf

# First build (15-30 minutes)
buildozer android debug

# APK: bin/pdfsplitter-1.0.0-debug.apk
```

See [BUILD_GUIDE.md](BUILD_GUIDE.md) for detailed instructions.

## 🔧 Configuration

### `buildozer.spec`
- **title**: App name (default: "PDF Splitter")
- **version**: Semantic version (default: 1.0.0)
- **android.api**: Target Android API (default: 29)
- **android.minapi**: Minimum Android API (default: 21)
- **orientation**: Screen orientation (default: portrait)

### `requirements.txt`
- **kivy**: 2.3.1 - UI framework
- **pymupdf**: 1.26.7 - PDF processing

## 📊 System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Android | 5.1 (API 21) | 9+ (API 29+) |
| RAM | 1GB | 2GB+ |
| Storage | 100MB free | 500MB+ free |
| Python | 3.8 | 3.11+ |

## 📚 Technologies

- **Python 3.11**: Application logic
- **Kivy 2.3.1**: Touch-optimized UI framework
- **PyMuPDF 1.26.7**: PDF processing library
- **Buildozer**: APK compilation
- **Android API 29**: Target platform

## 🐛 Troubleshooting

### Common Issues

**"App crashes on startup"**
- Ensure device has 100MB+ free storage
- Restart device
- Reinstall APK

**"Cannot find output files"**
- Location: `/sdcard/DCIM/PDFSplitter/`
- Use file manager app or `adb pull` command
- Check storage permissions

**"PDF not splitting / App freezes"**
- Close other running apps
- Try smaller PDF file first
- Check PDF is valid and not corrupted

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more issues and solutions.

## 📝 Testing

```bash
# Run unit tests
python test_app.py

# Test desktop version (development)
python main.py

# Expected output: 8/8 tests passing
```

## 🔄 CI/CD Pipeline

GitHub Actions automatically:
1. ✅ Builds APK on push to main/develop
2. ✅ Uploads as artifact (90-day retention)
3. ✅ Creates GitHub Release
4. ✅ Commits APK to repository
5. ✅ Posts build summary

See `.github/workflows/build-apk.yml` for details.

## 📄 License

[Include your license here]

## 🤝 Contributing

Contributions welcome! Please:
1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📞 Support

- **Issues**: GitHub Issues tab
- **Documentation**: See BUILD_GUIDE.md and TROUBLESHOOTING.md
- **Email**: [your-email]

## 🎯 Roadmap

- [ ] Release signing for Google Play Store
- [ ] Batch processing multiple PDFs
- [ ] OCR chapter detection
- [ ] Cloud storage integration
- [ ] Dark mode UI
- [ ] Multiple language support
- [ ] PDF compression options
- [ ] Chapter preview thumbnails

## 📈 Version History

### v1.0.0 (Current)
- Initial release
- Auto-detect chapters
- Manual page ranges
- Equal split functionality
- Professional touch UI

### Planned Releases
- v1.1.0: OCR and AI chapter detection
- v1.2.0: Cloud storage support
- v2.0.0: Batch processing and compression

---

**Made with ❤️ for PDF lovers**
