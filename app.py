"""
PDF Splitter with Chapter Detection
A Streamlit application to split PDFs by chapters or custom page ranges
"""

import streamlit as st
import pandas as pd
from src.pdf_processor import PDFProcessor, Chapter, parse_range_string
from src.gemini_detector import detect_chapters_with_gemini, validate_api_key
from src.utils import create_zip, format_file_size, generate_output_filename, validate_ranges, suggest_equal_splits


# Page configuration
st.set_page_config(
    page_title="PDF Splitter",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A5F;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .info-box {
        padding: 1rem;
        background-color: #e7f3ff;
        border-radius: 0.5rem;
        border-left: 4px solid #0066cc;
    }
    .warning-box {
        padding: 1rem;
        background-color: #fff3cd;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .chapter-card {
        padding: 0.75rem;
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
        border: 1px solid #dee2e6;
    }
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'pdf_processor' not in st.session_state:
        st.session_state.pdf_processor = None
    if 'pdf_info' not in st.session_state:
        st.session_state.pdf_info = None
    if 'chapters' not in st.session_state:
        st.session_state.chapters = []
    if 'split_files' not in st.session_state:
        st.session_state.split_files = None
    if 'gemini_api_key' not in st.session_state:
        st.session_state.gemini_api_key = ""


def render_header():
    """Render the app header"""
    st.markdown('<p class="main-header">✂️ PDF Splitter</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Split your PDF into multiple files by chapters or custom page ranges</p>', unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with options"""
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Gemini API Key (optional)
        st.subheader("🤖 AI Detection (Optional)")
        st.caption("Get free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)")
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            value=st.session_state.gemini_api_key,
            help="Enter your Gemini API key for AI-powered chapter detection"
        )
        st.session_state.gemini_api_key = api_key
        
        if api_key:
            if st.button("🔑 Validate API Key"):
                with st.spinner("Validating..."):
                    is_valid, message = validate_api_key(api_key)
                    if is_valid:
                        st.success(message)
                    else:
                        st.error(message)
        
        st.markdown("---")
        
        # Help section
        st.subheader("📖 How to Use")
        st.markdown("""
        1. **Upload** a PDF file
        2. **View** detected chapters or enter custom ranges
        3. **Edit** ranges - use + button to add rows anywhere
        4. **Split** and download as ZIP
        
        **Features:**
        - ✅ Auto-numbering (01_, 02_, etc.)
        - ✅ Add/remove chapters anywhere
        - ✅ AI-powered detection
        
        **Range Format:**
        - `1-10, 11-20, 21-30`
        - `1-10:Intro, 11-50:Main Content`
        """)
        
        st.markdown("---")
        st.caption("Made with ❤️ using Streamlit")


def render_upload_section():
    """Render the PDF upload section"""
    st.header("📤 Upload PDF")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF file to split"
    )
    
    if uploaded_file is not None:
        # Process the uploaded file
        if (st.session_state.pdf_info is None or 
            st.session_state.pdf_info.filename != uploaded_file.name):
            
            with st.spinner("Processing PDF..."):
                try:
                    pdf_bytes = uploaded_file.read()
                    processor = PDFProcessor(pdf_bytes, uploaded_file.name)
                    
                    # Initialize with default depth of 2
                    st.session_state.toc_depth = 2
                    info = processor.get_info(toc_depth=2)
                    
                    st.session_state.pdf_processor = processor
                    st.session_state.pdf_info = info
                    st.session_state.chapters = info.chapters.copy()
                    st.session_state.split_files = None
                    
                except Exception as e:
                    st.error(f"Error processing PDF: {str(e)}")
                    return
        
        return True
    else:
        # Clear state if no file
        st.session_state.pdf_processor = None
        st.session_state.pdf_info = None
        st.session_state.chapters = []
        st.session_state.split_files = None
        return False


def render_pdf_info():
    """Render PDF information section"""
    info = st.session_state.pdf_info
    
    st.header("📄 PDF Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📁 Filename", info.filename)
    
    with col2:
        st.metric("📃 Total Pages", info.total_pages)
    
    with col3:
        st.metric("💾 File Size", f"{info.file_size_mb:.2f} MB")
    
    # Show if TOC was found
    if info.has_toc:
        st.success("✅ Table of Contents detected in PDF!")
    elif info.chapters:
        st.info("🔍 Chapters detected by text analysis")
    else:
        st.warning("⚠️ No chapters detected. Use manual input or AI detection.")


def render_chapter_editor():
    """Render the chapter/range editor"""
    st.header("📑 Chapter Ranges")
    
    info = st.session_state.pdf_info
    
    # Detection method tabs
    tab1, tab2, tab3 = st.tabs(["📚 Detected Chapters", "✏️ Manual Input", "🤖 AI Detection"])
    
    with tab1:
        render_detected_chapters()
    
    with tab2:
        render_manual_input()
    
    with tab3:
        render_ai_detection()


def render_detected_chapters():
    """Render detected chapters with edit capability"""
    info = st.session_state.pdf_info
    chapters = st.session_state.chapters
    
    if not chapters:
        st.info("No chapters detected. Try manual input or AI detection.")
        
        # Quick split option
        st.subheader("Quick Split")
        num_parts = st.slider("Split into equal parts", 2, 10, 2)
        if st.button("Generate Equal Splits", key="equal_split_detected"):
            ranges = suggest_equal_splits(info.total_pages, num_parts)
            st.session_state.chapters = [
                Chapter(title=name, start_page=start, end_page=end)
                for start, end, name in ranges
            ]
            st.rerun()
        return
    
    st.write(f"Found **{len(chapters)}** chapters.")
    
    # Depth selector for TOC-based PDFs
    if info.has_toc:
        processor = st.session_state.pdf_processor
        max_depth = processor.get_toc_depth()
        
        if max_depth > 1:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"📚 This PDF has {max_depth} levels in the Table of Contents")
            with col2:
                # Initialize depth in session state if not present
                if 'toc_depth' not in st.session_state:
                    st.session_state.toc_depth = 2
                
                depth = st.selectbox(
                    "TOC Depth",
                    options=list(range(1, max_depth + 1)),
                    index=min(st.session_state.toc_depth - 1, max_depth - 1),
                    help="Select how many levels of the Table of Contents to include",
                    key="depth_selector"
                )
                
                if depth != st.session_state.toc_depth:
                    st.session_state.toc_depth = depth
                    # Reload chapters with new depth
                    new_info = processor.get_info(toc_depth=depth)
                    st.session_state.pdf_info = new_info
                    st.session_state.chapters = new_info.chapters.copy()
                    st.rerun()
    
    # Check for gaps and offer to fill them
    from src.utils import fill_missing_pages
    filled_ranges = fill_missing_pages(chapters, info.total_pages)
    
    if len(filled_ranges) > len(chapters):
        st.warning(f"⚠️ Some pages are not covered. Click 'Auto-Fill Gaps' to add missing pages.")
        if st.button("🔧 Auto-Fill Gaps", key="fill_gaps_btn"):
            st.session_state.chapters = [
                Chapter(title=name, start_page=start, end_page=end)
                for start, end, name in filled_ranges
            ]
            st.success("✅ Gaps filled!")
            st.rerun()
    
    st.info("💡 **Tip**: Click **+ Add row** at the bottom to add new chapters. Use ❌ to delete rows. Edit any cell directly.")
    
    # Create editable dataframe with index for reordering
    chapter_data = []
    for i, ch in enumerate(chapters, 1):
        chapter_data.append({
            "#": i,
            "Title": ch.title,
            "Start Page": ch.start_page,
            "End Page": ch.end_page,
            "Pages": ch.end_page - ch.start_page + 1
        })
    
    df = pd.DataFrame(chapter_data)
    
    # Editable table with better configuration
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        width="stretch",
        column_config={
            "#": st.column_config.NumberColumn("#", width="small", disabled=True, help="Auto-numbered"),
            "Title": st.column_config.TextColumn("Title", width="large", required=True),
            "Start Page": st.column_config.NumberColumn("Start Page", min_value=1, max_value=info.total_pages, required=True),
            "End Page": st.column_config.NumberColumn("End Page", min_value=1, max_value=info.total_pages, required=True),
            "Pages": st.column_config.NumberColumn("Pages", disabled=True, width="small")
        },
        hide_index=True,
        key="chapter_editor"
    )
    
    # Update chapters from edited dataframe
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("💾 Apply Changes", key="apply_detected", type="primary"):
            new_chapters = []
            for _, row in edited_df.iterrows():
                if pd.notna(row["Title"]) and pd.notna(row["Start Page"]) and pd.notna(row["End Page"]):
                    new_chapters.append(Chapter(
                        title=str(row["Title"]),
                        start_page=int(row["Start Page"]),
                        end_page=int(row["End Page"])
                    ))
            if new_chapters:
                st.session_state.chapters = new_chapters
                st.success("✅ Changes applied!")
                st.rerun()
            else:
                st.error("⚠️ No valid chapters found. Please add at least one chapter.")
    with col2:
        st.caption("Click + to add rows")


def render_manual_input():
    """Render manual range input with table editor"""
    info = st.session_state.pdf_info
    
    # Method selector
    method = st.radio(
        "Choose input method:",
        ["📊 Table Editor", "📝 Text Input", "⚡ Quick Split"],
        horizontal=True,
        key="manual_method"
    )
    
    st.markdown("---")
    
    if method == "⚡ Quick Split":
        # Quick split option
        st.write("Split document into equal parts:")
        num_parts = st.slider("Number of parts", 2, 20, 3, key="manual_parts")
        
        if st.button("Generate Equal Parts", key="gen_equal", type="primary"):
            ranges = suggest_equal_splits(info.total_pages, num_parts)
            st.session_state.chapters = [
                Chapter(title=name, start_page=start, end_page=end)
                for start, end, name in ranges
            ]
            st.success(f"✅ Generated {num_parts} equal parts!")
            st.rerun()
    
    elif method == "📊 Table Editor":
        # Table-based input (similar to detected chapters)
        st.write("Create chapters using the table editor:")
        
        # Initialize with current chapters or create a starter
        if not st.session_state.chapters:
            # Create a starter template
            chapter_data = [{
                "Title": "Chapter 1",
                "Start Page": 1,
                "End Page": info.total_pages,
                "Pages": info.total_pages
            }]
        else:
            chapter_data = []
            for ch in st.session_state.chapters:
                chapter_data.append({
                    "Title": ch.title,
                    "Start Page": ch.start_page,
                    "End Page": ch.end_page,
                    "Pages": ch.end_page - ch.start_page + 1
                })
        
        df = pd.DataFrame(chapter_data)
        
        st.info("💡 **Tip**: Click **+** to add more rows, ❌ to delete rows.")
        
        # Editable table
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            width="stretch",
            column_config={
                "Title": st.column_config.TextColumn("Title", width="large", required=True),
                "Start Page": st.column_config.NumberColumn("Start Page", min_value=1, max_value=info.total_pages, required=True),
                "End Page": st.column_config.NumberColumn("End Page", min_value=1, max_value=info.total_pages, required=True),
                "Pages": st.column_config.NumberColumn("Pages", disabled=True, width="small")
            },
            hide_index=True,
            key="manual_table_editor"
        )
        
        if st.button("💾 Apply Table Data", key="apply_manual_table", type="primary"):
            new_chapters = []
            for _, row in edited_df.iterrows():
                if pd.notna(row["Title"]) and pd.notna(row["Start Page"]) and pd.notna(row["End Page"]):
                    new_chapters.append(Chapter(
                        title=str(row["Title"]),
                        start_page=int(row["Start Page"]),
                        end_page=int(row["End Page"])
                    ))
            if new_chapters:
                st.session_state.chapters = new_chapters
                st.success(f"✅ Applied {len(new_chapters)} chapters!")
                st.rerun()
            else:
                st.error("⚠️ No valid chapters found. Please add at least one chapter.")
    
    else:  # Text Input
        # Text input for ranges
        st.write("Enter page ranges as text:")
        range_help = """
        **Format examples:**
        - `1-10, 11-20, 21-30` (auto-named as Part 1, Part 2, etc.)
        - `1-10:Introduction, 11-50:Main Content, 51-100:Appendix` (custom names)
        """
        st.markdown(range_help)
        
        # Generate default range string from current chapters
        default_range = ""
        if st.session_state.chapters:
            parts = [f"{ch.start_page}-{ch.end_page}:{ch.title}" for ch in st.session_state.chapters]
            default_range = ", ".join(parts)
        
        range_input = st.text_area(
            "Page Ranges",
            value=default_range,
            placeholder="1-10:Chapter 1, 11-25:Chapter 2, 26-50:Chapter 3",
            height=100,
            key="range_text_input"
        )
        
        if st.button("📥 Parse Ranges", key="parse_ranges", type="primary"):
            if range_input:
                try:
                    ranges = parse_range_string(range_input, info.total_pages)
                    if ranges:
                        st.session_state.chapters = [
                            Chapter(title=name, start_page=start, end_page=end)
                            for start, end, name in ranges
                        ]
                        st.success(f"✅ Parsed {len(ranges)} ranges!")
                        st.rerun()
                    else:
                        st.error("Could not parse any valid ranges. Check the format.")
                except Exception as e:
                    st.error(f"Error parsing ranges: {str(e)}")
            else:
                st.warning("Please enter some ranges first.")


def render_ai_detection():
    """Render AI-powered chapter detection"""
    info = st.session_state.pdf_info
    api_key = st.session_state.gemini_api_key
    
    if not api_key:
        st.warning("⚠️ Please enter your Gemini API key in the sidebar to use AI detection.")
        st.markdown("""
        **How to get an API key:**
        1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. Create a new API key
        3. Paste it in the sidebar
        """)
        return
    
    st.write("Use Gemini AI to automatically detect chapter boundaries.")
    
    st.info("""
    **How it works:**
    1. Extracts text from your PDF
    2. Sends it to Gemini AI for analysis
    3. AI identifies chapter/section boundaries
    4. You can edit the results before splitting
    """)
    
    if st.button("🤖 Detect Chapters with AI", key="ai_detect"):
        with st.spinner("Analyzing PDF with AI... This may take a moment."):
            try:
                processor = st.session_state.pdf_processor
                text_content = processor.get_text_for_ai(max_pages=30)
                
                chapters = detect_chapters_with_gemini(
                    text_content,
                    info.total_pages,
                    api_key
                )
                
                if chapters:
                    st.session_state.chapters = [
                        Chapter(
                            title=ch['title'],
                            start_page=ch['start_page'],
                            end_page=ch['end_page']
                        )
                        for ch in chapters
                    ]
                    st.success(f"✅ AI detected {len(chapters)} chapters!")
                    st.rerun()
                else:
                    st.warning("AI could not detect any chapters.")
                    
            except Exception as e:
                st.error(f"AI Detection Error: {str(e)}")


def render_split_section():
    """Render the split and download section"""
    st.header("✂️ Split & Download")
    
    chapters = st.session_state.chapters
    info = st.session_state.pdf_info
    
    if not chapters:
        st.warning("⚠️ Please define chapter ranges first.")
        return
    
    # Preview the splits
    st.subheader("Preview")
    st.caption("Files will be numbered automatically for easy tracking")
    
    preview_cols = st.columns(min(len(chapters), 4))
    for i, ch in enumerate(chapters, 1):
        with preview_cols[(i-1) % len(preview_cols)]:
            # Show how the file will be numbered
            num_digits = len(str(len(chapters)))
            prefix = f"{i:0{num_digits}d}_"
            st.markdown(f"""
            <div class="chapter-card">
                <strong style="color: #0066cc;">{prefix}</strong><strong>{ch.title}</strong><br>
                Pages {ch.start_page} - {ch.end_page}<br>
                <small>({ch.end_page - ch.start_page + 1} pages)</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Validate ranges
    ranges = [(ch.start_page, ch.end_page, ch.title) for ch in chapters]
    is_valid, error_msg = validate_ranges(ranges, info.total_pages)
    
    if not is_valid:
        st.error(f"⚠️ Invalid ranges: {error_msg}")
        return
    
    # Check coverage
    covered_pages = set()
    for ch in chapters:
        covered_pages.update(range(ch.start_page, ch.end_page + 1))
    
    missing_pages = set(range(1, info.total_pages + 1)) - covered_pages
    if missing_pages:
        missing_str = ', '.join(map(str, sorted(missing_pages)[:10]))
        if len(missing_pages) > 10:
            missing_str += f"... and {len(missing_pages) - 10} more"
        st.warning(f"⚠️ Some pages are not covered: {missing_str}")
    
    st.markdown("---")
    
    # Split button
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✂️ Split PDF", type="primary", key="split_btn"):
            with st.spinner("Splitting PDF..."):
                try:
                    processor = st.session_state.pdf_processor
                    split_files = processor.split_by_chapters(chapters)
                    st.session_state.split_files = split_files
                    st.success(f"✅ Successfully split into {len(split_files)} files!")
                except Exception as e:
                    st.error(f"Error splitting PDF: {str(e)}")
    
    # Download section
    if st.session_state.split_files:
        st.subheader("📥 Download")
        
        with col2:
            # Create ZIP
            zip_name = generate_output_filename(info.filename)
            zip_bytes = create_zip(st.session_state.split_files, zip_name)
            
            st.download_button(
                label=f"📦 Download ZIP ({len(st.session_state.split_files)} files)",
                data=zip_bytes,
                file_name=zip_name,
                mime="application/zip",
                type="primary"
            )
        
        # Individual file downloads
        with st.expander("Download Individual Files"):
            for filename, file_bytes in st.session_state.split_files:
                st.download_button(
                    label=f"📄 {filename}",
                    data=file_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    key=f"download_{filename}"
                )


def main():
    """Main application entry point"""
    init_session_state()
    render_header()
    render_sidebar()
    
    # Main content
    has_pdf = render_upload_section()
    
    if has_pdf and st.session_state.pdf_info:
        st.markdown("---")
        render_pdf_info()
        
        st.markdown("---")
        render_chapter_editor()
        
        st.markdown("---")
        render_split_section()


if __name__ == "__main__":
    main()
