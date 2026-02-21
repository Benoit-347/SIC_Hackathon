"""
Précis - AI-Powered Text Summarizer
A highly polished, modern Streamlit app for AI-powered text summarization.
Supports both file upload (.pdf, .txt) and direct text input.
"""

import streamlit as st
import time
from datetime import datetime
from io import BytesIO
import re
import math
import json
import os

st.set_page_config(
    page_title="Précis",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown("""
<style>
    /* Import Google Fonts for modern typography */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Mono:wght@300;400;500&display=swap');
    
    /* Color variables */
    :root {
        --bg: #0d0d0d;
        --surface: #111111;
        --border: #2a2a2a;
        --gold: #b5a06e;
        --gold-light: #cdb882;
        --text: #e8e4dc;
        --text-muted: #6e6a62;
        --text-dim: #5a5650;
    }
    
    /* Global styles */
    * {
        font-family: 'DM Mono', monospace;
    }
    
    /* Page load fade-in animation */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Slide-in animation for cards */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Scale animation for buttons */
    @keyframes scaleIn {
        from {
            opacity: 0;
            transform: scale(0.95);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    /* Main container with fade-in */
    .main .block-container {
        padding-top: 0;
        padding-bottom: 3rem;
        max-width: 1100px;
        animation: fadeIn 0.6s ease-out;
    }
    
    /* Gradient header banner with fade-in */
    .gradient-header {
        background: transparent;
        padding: 2rem 2.5rem 3rem 2.5rem;
        border-radius: 20px;
        margin-bottom: 2.5rem;
        margin-top: 0;
        box-shadow: none;
        color: white;
        animation: fadeIn 0.8s ease-out;
        position: relative;
        overflow: hidden;
        text-align: center;
    }
    
    .gradient-header::before {
        display: none;
    }
    
    .gradient-header h1 {
        font-family: 'Playfair Display', serif;
        font-size: clamp(2.6rem, 6vw, 4rem);
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.02em;
        color: #f0ebe0;
        text-shadow: 0 2px 20px rgba(0,0,0,0.15);
        position: relative;
        z-index: 1;
        line-height: 1.1;
    }
    
    .gradient-header p {
        font-size: 11px;
        margin: 0.6rem 0 0 0;
        color: var(--text-muted);
        font-weight: 400;
        position: relative;
        z-index: 1;
        letter-spacing: 0.08em;
    }
    
    /* Large section headings - bold and dominant */
    .section-heading {
        font-family: 'DM Mono', monospace;
        font-size: 10px;
        font-weight: 400;
        color: var(--gold);
        margin: 2rem 0 0.8rem 0;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        animation: slideIn 0.5s ease-out;
        line-height: 1.2;
    }
    
    .section-heading-small {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        margin: 1.5rem 0 1rem 0;
        letter-spacing: -0.01em;
        animation: slideIn 0.5s ease-out;
    }
    
    /* Card containers with soft shadows and slide-in */
    .premium-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 25px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.04);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: slideIn 0.6s ease-out;
    }
    
    .premium-card:hover {
        box-shadow: 0 8px 35px rgba(0,0,0,0.12);
        transform: translateY(-3px);
    }
    
    /* Summary output card with reveal animation */
    .summary-card {
        background: black;
        border: 2px solid #e2e8f0;
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 8px 30px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
        animation: fadeIn 0.7s ease-out;
    }
    
    .summary-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 5px;
        height: 100%;
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Stats badges */
    .stat-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: #b5a06e;
        color: white;
        padding: 0.5rem 1.25rem;
        border-radius: 3px;
        font-family: 'DM Mono', monospace;
        font-size: 10px;
        font-weight: 400;
        letter-spacing: 0.1em;
        margin-right: 1rem;
        margin-bottom: 1rem;
        border: 1px solid var(--border);
        transition: transform 0.2s ease;
    }
    
    .stat-badge:hover {
        transform: scale(1.05);
    }
    
    /* Premium button styling with scale and glow */
    .stButton > button {
        background: var(--gold);
        color: var(--bg);
        border: none;
        border-radius: 3px;
        padding: 0.75rem 1.5rem;
        font-family: 'DM Mono', monospace;
        font-weight: 400;
        font-size: 11px;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        transition: background 0.2s, transform 0.1s;
        box-shadow: 0 6px 20px rgba(181, 160, 110, 0.3);
        width: 100%;
        animation: scaleIn 0.5s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.2);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 10px 30px rgba(181, 160, 110, 0.5), 0 0 20px rgba(181, 160, 110, 0.3);
        background: var(--gold-light);
    }
    
    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) scale(1);
    }
    
    /* Secondary button */
    .secondary-btn {
        background: var(--surface) !important;
        color: var(--gold) !important;
        border: 2px solid var(--gold) !important;
        box-shadow: 0 3px 12px rgba(181, 160, 110, 0.2) !important;
    }
    
    .secondary-btn:hover {
        background: var(--bg) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 18px rgba(181, 160, 110, 0.3) !important;
    }
    
    /* Download button styling */
    .stDownloadButton > button {
        background: transparent !important;
        color: var(--gold) !important;
        border: 1px solid var(--gold) !important;
        border-radius: 3px !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 11px !important;
        letter-spacing: 0.2em !important;
        text-transform: uppercase !important;
        padding: 0.65rem 1.5rem !important;
        transition: background 0.2s !important;
    }
    
    .stDownloadButton > button:hover {
        background: rgba(181, 160, 110, 0.1) !important;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: #f8fafc;
    }
    
    /* Hide sidebar close/collapse button */
    [data-testid="stSidebar"] [data-testid="collapsedControl"],
    [data-testid="stSidebar"] button[aria-label="Close sidebar"],
    [data-testid="stSidebar"] button[aria-label="Close navigation"],
    [data-testid="stSidebar"] button[aria-label="Open sidebar"],
    button[data-testid="baseButton-header"],
    [data-testid="stHeader"] button,
    [data-testid="stToolbar"] button,
    [data-testid="stHeader"] [data-testid="stHeaderToolbar"] button,
    [data-testid="stSidebar"] > button,
    section[data-testid="stSidebar"] button {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }
    
    /* History items with slide-in */
    .history-card {
        background: white;
        border-radius: 14px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        animation: slideIn 0.4s ease-out;
    }
    
    .history-card:hover {
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
        transform: translateX(6px);
        border-left-color: #764ba2;
    }
    
    .history-title {
        font-weight: 700;
        color: #1e293b;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
    }
    
    .history-preview {
        color: #64748b;
        font-size: 0.85rem;
        margin: 0.5rem 0;
        line-height: 1.5;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    
    .history-time {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    /* Upload section - dark royal blue drop box, large drag-and-drop */
    .upload-section-heading {
        font-size: 2.25rem;
        font-weight: 700;
        color: #1e293b;
        margin: 2rem 0 1.5rem 0;
        letter-spacing: -0.02em;
        animation: slideIn 0.5s ease-out;
    }
    
    [data-testid="stFileUploader"] {
        border: 2px dashed #60a5fa !important;
        border-radius: 16px !important;
        padding: 3rem 2rem !important;
        min-height: 180px !important;
        background: #1e3a8a !important;
        box-shadow: 0 4px 24px rgba(30, 58, 138, 0.35);
        transition: all 0.3s ease-in-out !important;
        animation: fadeIn 0.6s ease-out;
    }
    
    [data-testid="stFileUploader"]:hover {
        background: #233876 !important;
        border-color: #93c5fd !important;
        box-shadow: 0 6px 28px rgba(30, 58, 138, 0.45), 0 0 0 1px rgba(147, 197, 253, 0.2);
    }
    
    [data-testid="stFileUploader"] section {
        background: transparent !important;
    }
    
    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] label p {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stFileUploader"] small {
        color: rgba(255, 255, 255, 0.88) !important;
        font-weight: 500;
    }
    
    /* Selected files - card list */
    .file-card {
        background: white;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
        border: 1px solid #e2e8f0;
        display: flex;
        align-items: center;
        gap: 1rem;
        transition: all 0.25s ease;
        animation: slideIn 0.4s ease-out;
    }
    
    .file-card:hover {
        box-shadow: 0 4px 18px rgba(59, 130, 246, 0.15);
        transform: translateY(-1px);
    }
    
    .file-card-icon {
        width: 44px;
        height: 44px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.85rem;
        color: white;
        flex-shrink: 0;
    }
    
    .file-card-icon.pdf {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    }
    
    .file-card-icon.txt {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    }
    
    .file-card-name {
        font-weight: 600;
        color: #1e293b;
        font-size: 0.95rem;
        flex: 1;
        word-break: break-word;
    }
    
    .file-card-size {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 500;
    }
    
    /* Responsive - stack on small screens */
    @media (max-width: 768px) {
        .file-card {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
        }
        .file-card-size {
            margin-left: 54px;
        }
        .upload-section-heading {
            font-size: 1.75rem;
        }
    }
    
    @media (max-width: 480px) {
        [data-testid="stFileUploader"] {
            padding: 2rem 1rem !important;
            min-height: 140px !important;
        }
    }
    
    /* Text area styling */
    .stTextArea > div > div > textarea {
        background: var(--surface);
        color: var(--text);
        border-radius: 4px;
        border: 1px solid var(--border);
        font-family: 'DM Mono', monospace;
        font-size: 13px;
        line-height: 1.7;
        transition: border-color 0.2s, box-shadow 0.2s;
        animation: fadeIn 0.5s ease-out;
    }
    
    .stTextArea > div > div > textarea::placeholder {
        color: var(--text-dim);
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: var(--gold);
        box-shadow: 0 0 0 2px rgba(181, 160, 110, 0.13);
        outline: none;
    }
    
    /* Character counter */
    .char-counter {
        font-family: 'DM Mono', monospace;
        font-size: 10px;
        color: var(--text-dim);
        text-align: right;
        margin-top: 0.75rem;
        font-weight: 400;
        letter-spacing: 0.1em;
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Footer */
    .footer {
        margin-top: 5rem;
        padding-top: 2rem;
        border-top: 1px solid #e2e8f0;
        text-align: center;
        color: #64748b;
        font-size: 0.9rem;
        font-weight: 500;
        animation: fadeIn 0.8s ease-out;
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 3rem 2rem;
        color: #94a3b8;
        animation: fadeIn 0.6s ease-out;
    }
    
    .empty-state-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 14px 14px 0 0;
        padding: 1rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #f8fafc;
    }
    
    /* Expander styling for history */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 14px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transform: translateX(3px);
    }
    
    .streamlit-expanderContent {
        background: #f8fafc;
        border-radius: 0 0 14px 14px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
    }
    
    /* Scrollable preview */
    .preview-container {
        background: #f8fafc;
        border: 2px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.5rem;
        max-height: 350px;
        overflow-y: auto;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        line-height: 1.7;
        color: black;
        animation: fadeIn 0.6s ease-out;
    }
    
    /* Smooth transitions for all interactive elements */
    button, input, textarea, select {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)



# Session state initialization

def init_session_state():
    """Initialize all session state keys."""
    defaults = {
        "summary_history": [],
        "current_file_name": None,
        "current_extracted_text": "",
        "manual_input_text": "",
        "last_summary": "",
        "input_source": "file",  # "file" or "manual"
        "last_uploaded_names": [],  # track processed file names for progress
    }
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # Load history from file if it exists and session history is empty
    if not st.session_state.summary_history:
        file_history = load_history_from_file()
        if file_history:
            st.session_state.summary_history = file_history



# File reading and text extraction

def extract_text_from_txt(file) -> str:
    """Extract text from an uploaded .txt file."""
    try:
        return file.getvalue().decode("utf-8", errors="replace")
    except Exception as e:
        return f"[Error reading file: {e}]"


def extract_text_from_pdf(file) -> str:
    """Extract text from an uploaded PDF file using pypdf."""
    try:
        import pypdf
        reader = pypdf.PdfReader(BytesIO(file.getvalue()))
        text_parts = []
        for page in reader.pages:
            text_parts.append(page.extract_text() or "")
        extracted = "\n\n".join(text_parts).strip()
        return extracted if extracted else "[No text could be extracted from this PDF.]"
    except ImportError:
        return "[PDF support requires 'pypdf'. Install with: pip install pypdf]"
    except Exception as e:
        return f"[Error extracting PDF text: {e}]"


def extract_text_from_file(uploaded_file) -> str:
    """Dispatch to appropriate extractor based on file type."""
    if uploaded_file is None:
        return ""
    name = (uploaded_file.name or "").lower()
    if name.endswith(".txt"):
        return extract_text_from_txt(uploaded_file)
    elif name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    return "[Unsupported file type. Use .txt or .pdf]"


# ---------------------------------------------------------------------------
# Summary generation (placeholder - replace with backend AI later)
# ---------------------------------------------------------------------------
def summarize_text(text: str, max_sentences: int = 6) -> str:
    """
    Generate a summary from the given text.
    PLACEHOLDER: Uses first N sentences. Replace this with your AI/backend call.
    """
    if not text or text.startswith("[") or len(text.strip()) < 10:
        return "No content available to summarize. Please provide valid text."
    
    # Simple sentence boundary detection
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return text[:500] + "..." if len(text) > 500 else text
    
    summary = " ".join(sentences[:max_sentences])
    return summary.strip()


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------
def calculate_reading_time(text: str, words_per_minute: int = 200) -> str:
    """Calculate estimated reading time in minutes."""
    word_count = len(text.split())
    minutes = math.ceil(word_count / words_per_minute)
    if minutes < 1:
        return "< 1 min"
    return f"{minutes} min"


# ---------------------------------------------------------------------------
# History management
# ---------------------------------------------------------------------------
HISTORY_FILE = "summary_history.json"

def load_history_from_file():
    """Load history from JSON file."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_history_to_file(history_list):
    """Save history list to JSON file."""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history_list, f, ensure_ascii=False, indent=2)
    except IOError as e:
        st.error(f"Error saving history: {e}")


def save_to_history(source_name: str, summary: str):
    """Save a summary entry to session history and persistent file."""
    entry = {
        "source_name": source_name,
        "summary_preview": (summary[:150] + "…") if len(summary) > 150 else summary,
        "full_summary": summary,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    st.session_state.summary_history.insert(0, entry)
    # Keep last 50 entries
    st.session_state.summary_history = st.session_state.summary_history[:50]
    # Save to file
    save_history_to_file(st.session_state.summary_history)


def clear_history():
    """Clear all summary history from session and file."""
    st.session_state.summary_history = []
    save_history_to_file([])


# ---------------------------------------------------------------------------
# UI Components
# ---------------------------------------------------------------------------
def render_gradient_header():
    """Render the premium gradient header banner."""
    st.markdown("""
    <div class="gradient-header">
        <h1>Précis</h1>
        <p>Intelligent text condensation · Powered by Llama 3.3 · 70B</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render the Dashboard sidebar with summary history."""
    with st.sidebar:
        st.markdown("### Dashboard")
        st.markdown("---")
        
        if not st.session_state.summary_history:
            st.markdown("""
            <div class="empty-state">
                <p>No summaries yet.<br>Generate your first summary!</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for i, entry in enumerate(st.session_state.summary_history):
                with st.expander(f"{entry['source_name']} - {entry['timestamp']}", expanded=False):
                    st.markdown(f"**Preview:** {entry['summary_preview']}")
                    st.markdown("---")
                    st.markdown("**Full Summary:**")
                    st.text_area(
                        "Summary content",
                        value=entry['full_summary'],
                        height=150,
                        disabled=True,
                        label_visibility="collapsed",
                        key=f"history_summary_{i}"
                    )
        

        if st.button("Clear History", use_container_width=True, type="secondary"):
            clear_history()
            st.rerun()


def render_footer():
    """Render the app footer."""
    st.markdown("""
    <div class="footer">
        Built with Streamlit | Précis © 2026
    </div>
    """, unsafe_allow_html=True)


def _format_file_size(size_bytes: int) -> str:
    """Format file size for display (KB or MB)."""
    size_kb = size_bytes / 1024
    if size_kb >= 1024:
        return f"{size_kb / 1024:.2f} MB"
    return f"{size_kb:.1f} KB"


def _file_icon_class(filename: str) -> str:
    """Return CSS class for file icon (pdf or txt)."""
    return "pdf" if (filename or "").lower().endswith(".pdf") else "txt"


def render_file_upload_tab():
    """Render the file upload tab with multiple file support and styled upload zone."""
    st.markdown('<h2 class="upload-section-heading">Upload Files</h2>', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Drag and drop files here or click to browse",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        help="Supported formats: PDF and TXT. You can select multiple files.",
        label_visibility="visible",
    )
    
    if uploaded_files:
        current_names = sorted(f.name for f in uploaded_files)
        # Run progress bar and extract only when file set changed
        if st.session_state.get("last_uploaded_names") != current_names:
            progress_bar = st.progress(0, text="Processing files...")
            steps = 50
            for i in range(1, steps + 1):
                time.sleep(0.02)
                progress_bar.progress(i / steps, text=f"Processing files... {int(100 * i / steps)}%")
            # Extract text from all files and combine
            combined_parts = []
            for f in uploaded_files:
                combined_parts.append(extract_text_from_file(f))
            combined_text = "\n\n".join(combined_parts).strip()
            st.session_state.current_extracted_text = combined_text
            st.session_state.current_file_name = ", ".join(f.name for f in uploaded_files)
            st.session_state.last_uploaded_names = current_names
            st.session_state.input_source = "file"
            progress_bar.progress(1.0, text="Done")
            time.sleep(0.2)
            progress_bar.empty()
        
        # Selected files display - card list
        st.markdown('<p class="section-heading-small" style="margin-top: 1.5rem;">Selected Files</p>', unsafe_allow_html=True)
        for f in uploaded_files:
            size_str = _format_file_size(len(f.getvalue()))
            icon_class = _file_icon_class(f.name)
            # Use simple text label for PDF/TXT (Unicode-style)
            icon_label = "PDF" if icon_class == "pdf" else "TXT"
            st.markdown(
                f'<div class="file-card">'
                f'<span class="file-card-icon {icon_class}">{icon_label}</span>'
                f'<span class="file-card-name">{f.name}</span>'
                f'<span class="file-card-size">{size_str}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        
        # Extracted text preview
        extracted = st.session_state.current_extracted_text
        if extracted and not extracted.startswith("["):
            st.markdown('<h3 class="section-heading-small">Extracted Text Preview</h3>', unsafe_allow_html=True)
            preview = extracted[:2000] + ("..." if len(extracted) > 2000 else "")
            st.markdown(f'<div class="preview-container">{preview}</div>', unsafe_allow_html=True)
        elif extracted.startswith("["):
            st.error(extracted)
    else:
        st.session_state.current_file_name = None
        st.session_state.current_extracted_text = ""
        st.session_state.last_uploaded_names = []


def render_manual_input_tab():
    """Render the manual text input tab."""
    st.markdown('<h2 class="section-heading">Enter Text</h2>', unsafe_allow_html=True)
    
    placeholder_text = """Enter or paste your text here. For example:

Artificial intelligence (AI) is transforming industries across the globe. From healthcare to finance, AI technologies are enabling unprecedented levels of automation and insight. Machine learning algorithms can now process vast amounts of data to identify patterns that would be impossible for humans to detect. As we continue to develop more sophisticated AI systems, the potential applications seem limitless."""
    
    manual_text = st.text_area(
        "Your text content",
        value=st.session_state.manual_input_text,
        height=500,
        placeholder=placeholder_text,
        label_visibility="collapsed",
        key="manual_text_input",
    )
    
    st.session_state.manual_input_text = manual_text
    
    # Character counter
    char_count = len(manual_text)
    word_count = len(manual_text.split()) if manual_text.strip() else 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="char-counter">Characters: {char_count:,}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="char-counter">Words: {word_count:,}</div>', unsafe_allow_html=True)
    
    if manual_text.strip():
        st.session_state.input_source = "manual"
    else:
        st.info("Enter your text above to get started.")


def render_summarization_section():
    """Render the summarization button and processing."""
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        generate_clicked = st.button("Generate Summary", type="primary", use_container_width=True)
    
    return generate_clicked


def render_summary_output(summary: str, original_text: str = ""):
    """Render the summary output card with stats."""
    # Only render if there's actually a summary to display
    if not summary or not summary.strip():
        return
    
    st.markdown('<h2 class="section-heading">Summary Output</h2>', unsafe_allow_html=True)
    
    summary_word_count = len(summary.split())
    original_word_count = len(original_text.split()) if original_text and original_text.strip() else 0
    
    st.markdown(f"""
    <div class="summary-card">
        <div>
            <span class="stat-badge">Number of words: {original_word_count:,}</span>
            <span class="stat-badge">Number of summary words: {summary_word_count:,}</span>
        </div>
        <div style="margin-top: 1.5rem; line-height: 1.8; color: #ddd8cc; font-size: 0.85rem; font-family: 'DM Mono', monospace; white-space: pre-wrap;">
            {summary}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Download button
    st.download_button(
        label="⬇ Download Summary (.txt)",
        data=summary,
        file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
        use_container_width=True,
        type="secondary"
    )


# ---------------------------------------------------------------------------
# Main App
# ---------------------------------------------------------------------------
def main():
    init_session_state()
    
    # Sidebar
    render_sidebar()
    
    # Header
    render_gradient_header()
    
    # Main content tabs
    tab1, tab2 = st.tabs(["Upload File", "Enter Text"])
    
    with tab1:
        render_file_upload_tab()
    
    with tab2:
        render_manual_input_tab()
    
    # Get current text based on input source
    current_text = ""
    source_name = "Manual Input"
    
    if st.session_state.input_source == "file":
        current_text = st.session_state.current_extracted_text
        source_name = st.session_state.current_file_name or "Uploaded Document"
    else:
        current_text = st.session_state.manual_input_text
        source_name = "Manual Input"
    
    # Summarization section
    generate_clicked = render_summarization_section()
    
    # Process summarization
    summary_output = st.session_state.last_summary
    
    if generate_clicked:
        if current_text and current_text.strip() and not current_text.startswith("["):
            with st.spinner("Processing your content with AI..."):
                summary_output = summarize_text(current_text)
                st.session_state.last_summary = summary_output
                save_to_history(source_name, summary_output)
                st.rerun()
        else:
            st.warning("Please provide text content first (upload a file or paste text).")
    
    # Summary output
    render_summary_output(st.session_state.last_summary, current_text)
    
    # Footer
    render_footer()
if __name__ == "__main__":
    main()