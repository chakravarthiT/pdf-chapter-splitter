# PDF Splitter with Chapter Detection - Design Document

## 📋 Project Overview

A web application that allows users to upload PDFs and split them into multiple files based on:
- Manual page ranges
- Auto-detected chapters (using PDF bookmarks/TOC)
- AI-powered chapter detection (optional, using Gemini API)

---

## 🎯 Features Summary

| Feature | Priority | Description |
|---------|----------|-------------|
| PDF Upload | High | Drag & drop or click to upload PDF |
| Page Range Display | High | Show total pages, allow manual range input |
| Bookmark Detection | High | Auto-detect chapters from PDF bookmarks/TOC |
| Manual Range Split | High | User enters ranges like "1-5, 6-10, 11-20" |
| Gemini AI Detection | Medium | Use AI to detect chapter boundaries (optional) |
| ZIP Download | High | Download all split PDFs as a single ZIP |
| Preview | Low | Preview pages before splitting |

---

## 🏗️ Architecture Options

### Option A: Streamlit (Recommended ✅)

**Pros:**
- Fast to develop
- Built-in file upload/download
- No separate frontend needed
- Easy deployment (Streamlit Cloud, free tier available)
- Python-native

**Cons:**
- Limited customization
- Can't deploy to GitHub Pages (requires server)

**Deployment:** Streamlit Cloud (free), Heroku, Railway, or any Python host

---

### Option B: Static Frontend + Python Backend (FastAPI)

**Pros:**
- GitHub Pages compatible (frontend only)
- More customizable UI
- Can use modern frameworks (React, Vue, vanilla JS)

**Cons:**
- Need separate backend hosting
- More complex setup
- CORS handling required

**Deployment:** 
- Frontend: GitHub Pages
- Backend: Render, Railway, Vercel (serverless), or any Python host

---

### Option C: Fully Client-Side (JavaScript)

**Pros:**
- 100% GitHub Pages compatible
- No server costs
- Works offline

**Cons:**
- Limited PDF manipulation libraries in JS
- Gemini API key exposed in browser (security risk)
- You mentioned preference for Python

---

## 💡 Recommendation

**Go with Option A (Streamlit)** because:
1. You're familiar with Python
2. Fastest to develop and iterate
3. Free deployment on Streamlit Cloud
4. All features can be implemented easily
5. No need to manage frontend/backend separately

---

## 📁 Proposed Project Structure

```
split-pdf-with-chapters/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── src/
│   ├── __init__.py
│   ├── pdf_processor.py    # PDF reading, splitting logic
│   ├── chapter_detector.py # Bookmark/TOC extraction
│   ├── gemini_detector.py  # AI-based chapter detection
│   └── utils.py            # Helper functions (ZIP creation, etc.)
├── docs/
│   └── DESIGN.md           # This document
├── .gitignore
├── .streamlit/
│   └── config.toml         # Streamlit configuration
└── README.md               # Project documentation
```

---

## 🔧 Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend/UI | Streamlit |
| PDF Processing | PyPDF2 or pypdf |
| Chapter Detection | PyPDF2 (bookmarks) + pdfplumber (TOC) |
| AI Detection | Google Generative AI (Gemini) |
| ZIP Creation | Python zipfile module |
| Deployment | Streamlit Cloud |

---

## 📊 User Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        PDF SPLITTER APP                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. UPLOAD PDF                                                  │
│     ┌─────────────────────────────────────┐                     │
│     │  📁 Drag & Drop or Click to Upload  │                     │
│     └─────────────────────────────────────┘                     │
│                           ▼                                     │
│  2. VIEW PDF INFO                                               │
│     ┌─────────────────────────────────────┐                     │
│     │  📄 filename.pdf                    │                     │
│     │  Pages: 150                         │                     │
│     │  Detected Chapters: 5               │                     │
│     └─────────────────────────────────────┘                     │
│                           ▼                                     │
│  3. CHOOSE SPLIT METHOD                                         │
│     ┌─────────────────────────────────────┐                     │
│     │  ○ Use Detected Chapters            │                     │
│     │  ○ Manual Range Input               │                     │
│     │  ○ AI Detection (Gemini)            │                     │
│     └─────────────────────────────────────┘                     │
│                           ▼                                     │
│  4. CONFIGURE RANGES                                            │
│     ┌─────────────────────────────────────┐                     │
│     │  Chapter 1: Pages 1-25    [Edit]    │                     │
│     │  Chapter 2: Pages 26-50   [Edit]    │                     │
│     │  Chapter 3: Pages 51-80   [Edit]    │                     │
│     │  [+ Add Range]                      │                     │
│     └─────────────────────────────────────┘                     │
│                           ▼                                     │
│  5. SPLIT & DOWNLOAD                                            │
│     ┌─────────────────────────────────────┐                     │
│     │  [🔪 Split PDF]  [📦 Download ZIP]  │                     │
│     └─────────────────────────────────────┘                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Feature Details

### 1. PDF Upload & Info Display
- Accept PDF files up to 200MB
- Display: filename, page count, file size
- Extract and show existing bookmarks/chapters

### 2. Auto Chapter Detection (from PDF metadata)
```python
# Using PyPDF2 to extract bookmarks
from pypdf import PdfReader

reader = PdfReader("document.pdf")
bookmarks = reader.outline  # Returns bookmark tree
```

### 3. Manual Range Input
- Text input: `1-10, 11-25, 26-50`
- Or dynamic form with start/end page inputs
- Validation to ensure ranges don't overlap and cover all pages

### 4. AI-Powered Detection (Gemini)
- Extract text from first few lines of each page
- Send to Gemini to identify chapter boundaries
- Parse response and suggest ranges
- **Note:** This requires API key (user provides their own)

### 5. Split & ZIP Download
```python
from pypdf import PdfReader, PdfWriter
import zipfile

# Split logic
for i, (start, end) in enumerate(ranges):
    writer = PdfWriter()
    for page_num in range(start-1, end):
        writer.add_page(reader.pages[page_num])
    writer.write(f"chapter_{i+1}.pdf")

# Create ZIP
with zipfile.ZipFile("output.zip", "w") as zf:
    for file in pdf_files:
        zf.write(file)
```

---

## 🚀 Development Phases

### Phase 1: Core Functionality (MVP)
- [ ] Basic Streamlit UI
- [ ] PDF upload
- [ ] Display page count
- [ ] Manual range input
- [ ] Split PDF
- [ ] Download individual files

### Phase 2: Auto Detection
- [ ] Extract bookmarks from PDF
- [ ] Display detected chapters
- [ ] Allow editing detected ranges

### Phase 3: AI Integration
- [ ] Gemini API integration
- [ ] API key input (secure)
- [ ] AI-suggested chapter boundaries

### Phase 4: Polish
- [ ] ZIP download
- [ ] Better UI/UX
- [ ] Error handling
- [ ] Progress indicators
- [ ] Preview functionality

---

## ❓ Questions to Discuss

1. **Deployment preference?**
   - Streamlit Cloud (free, easiest)
   - Self-hosted
   - Other platform?

2. **File size limits?**
   - What's the max PDF size you expect to handle?

3. **Chapter naming convention?**
   - `chapter_1.pdf`, `chapter_2.pdf`
   - Use actual chapter names from bookmarks?
   - Custom naming?

4. **Error handling?**
   - What should happen if PDF is password-protected?
   - What if no chapters are detected?

5. **Do you want page preview?**
   - Show thumbnail of pages?
   - This adds complexity but improves UX

---

## ✅ Next Steps

Once you approve this design:

1. I'll set up the project structure
2. Implement Phase 1 (MVP)
3. Test locally
4. Add Phase 2 & 3 features
5. Deploy to Streamlit Cloud

---

**Please review and let me know:**
- Any changes to the approach?
- Answers to the questions above?
- Ready to start coding?
