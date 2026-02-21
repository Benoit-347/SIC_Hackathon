"""
Précis - AI-Powered Text Summarizer & Chat
A highly polished, modern Streamlit app for AI-powered text summarization.
Integrated with Groq (Llama 3.3), Google Translator, RapidOCR, and Chat Memory.
"""

import streamlit as st
import time
from datetime import datetime
from io import BytesIO
import re
import math
import json
import os
import textwrap
import tempfile
from collections import deque

# --- Backend Dependencies ---
from deep_translator import GoogleTranslator
from rapidocr_pdf import RapidOCRPDF
from groq import Groq

# ---------------------------------------------------------------------------
# App Configuration & CSS
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Précis",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Mono:wght@300;400;500&display=swap');
    
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
    
    * { font-family: 'DM Mono', monospace; }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes scaleIn {
        from { opacity: 0; transform: scale(0.95); }
        to { opacity: 1; transform: scale(1); }
    }
    
    .main .block-container {
        padding-top: 0;
        padding-bottom: 3rem;
        max-width: 1100px;
        animation: fadeIn 0.6s ease-out;
    }
    
    .gradient-header {
        background: transparent;
        padding: 2rem 2.5rem 3rem 2.5rem;
        border-radius: 20px;
        margin-bottom: 2.5rem;
        margin-top: 0;
        text-align: center;
        animation: fadeIn 0.8s ease-out;
    }
    
    .gradient-header h1 {
        font-family: 'Playfair Display', serif;
        font-size: clamp(2.6rem, 6vw, 4rem);
        font-weight: 700;
        margin: 0;
        color: #f0ebe0;
        text-shadow: 0 2px 20px rgba(0,0,0,0.15);
    }
    
    .gradient-header p {
        font-size: 11px;
        margin: 0.6rem 0 0 0;
        color: var(--text-muted);
        letter-spacing: 0.08em;
    }
    
    .section-heading {
        font-size: 10px;
        font-weight: 400;
        color: var(--gold);
        margin: 2rem 0 0.8rem 0;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        animation: slideIn 0.5s ease-out;
    }
    
    .section-heading-small {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        margin: 1.5rem 0 1rem 0;
        animation: slideIn 0.5s ease-out;
    }
    
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
    
    .stat-badge {
        display: inline-flex;
        align-items: center;
        background: #b5a06e;
        color: white;
        padding: 0.5rem 1.25rem;
        border-radius: 3px;
        font-size: 10px;
        letter-spacing: 0.1em;
        margin-right: 1rem;
        margin-bottom: 1rem;
    }
    
    .stButton > button {
        background: var(--gold);
        color: var(--bg);
        border: none;
        border-radius: 3px;
        padding: 0.75rem 1.5rem;
        font-size: 11px;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        transition: all 0.2s;
        box-shadow: 0 6px 20px rgba(181, 160, 110, 0.3);
        width: 100%;
        animation: scaleIn 0.5s ease-out;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 10px 30px rgba(181, 160, 110, 0.5);
        background: var(--gold-light);
    }
    
    .stDownloadButton > button {
        background: transparent !important;
        color: var(--gold) !important;
        border: 1px solid var(--gold) !important;
    }
    
    .sidebar .sidebar-content { background: #f8fafc; }
    
    /* Hide specific Streamlit elements to maintain clean UI */
    [data-testid="stSidebar"] [data-testid="collapsedControl"],
    button[data-testid="baseButton-header"],
    #MainMenu, footer, header { display: none !important; }
    
    .upload-section-heading {
        font-size: 2.25rem;
        font-weight: 700;
        color: #1e293b;
        margin: 2rem 0 1.5rem 0;
        animation: slideIn 0.5s ease-out;
    }
    
    [data-testid="stFileUploader"] {
        border: 2px dashed #60a5fa !important;
        border-radius: 16px !important;
        padding: 3rem 2rem !important;
        background: #1e3a8a !important;
        transition: all 0.3s ease-in-out !important;
    }
    
    [data-testid="stFileUploader"]:hover {
        background: #233876 !important;
        border-color: #93c5fd !important;
    }
    
    [data-testid="stFileUploader"] label p { color: #ffffff !important; }
    
    .file-card {
        background: white;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        border: 1px solid #e2e8f0;
        display: flex;
        align-items: center;
        gap: 1rem;
        animation: slideIn 0.4s ease-out;
    }
    
    .file-card-icon {
        width: 44px;
        height: 44px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        color: white;
    }
    
    .file-card-icon.pdf { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }
    .file-card-icon.txt { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); }
    
    .file-card-name { font-weight: 600; color: #1e293b; flex: 1; }
    .file-card-size { color: #64748b; font-size: 0.85rem; }
    
    .stTextArea > div > div > textarea {
        background: var(--surface);
        color: var(--text);
        border: 1px solid var(--border);
        font-size: 13px;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: var(--gold);
        box-shadow: 0 0 0 2px rgba(181, 160, 110, 0.13);
    }
    
    .preview-container {
        background: #f8fafc;
        border: 2px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.5rem;
        max-height: 350px;
        overflow-y: auto;
        font-family: 'Courier New', monospace;
        color: black;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Backend Logic & State Management
# ---------------------------------------------------------------------------
HISTORY_FILE = "summary_history.json"

class FastContextManager:
    def __init__(self, max_words=8000):
        self.messages = deque()
        self.current_word_count = 0
        self.max_words = max_words
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def _count_words(self, text: str) -> int:
        return len(text.split())

    def add_message(self, role: str, content: str):
        word_count = self._count_words(content)
        self.messages.append({"role": role, "content": content, "words": word_count})
        self.current_word_count += word_count

        while self.current_word_count > self.max_words and len(self.messages) > 1:
            oldest_msg = self.messages.popleft()
            self.current_word_count -= oldest_msg["words"]

    def generate_response(self, user_prompt: str) -> str:
        self.add_message("user", user_prompt)
        api_payload = [{"role": msg["role"], "content": msg["content"]} for msg in self.messages]

        try:
            chat_completion = self.client.chat.completions.create(
                messages=api_payload,
                model="llama-3.3-70b-versatile", 
            )
            response_text = chat_completion.choices[0].message.content
            self.add_message("assistant", response_text)
            return response_text
        except Exception as e:
            return f"[Error connecting to Groq API: {e}]"


def init_session_state():
    defaults = {
        "summary_history": [],
        "current_file_name": None,
        "current_extracted_text": "",
        "manual_input_text": "",
        "last_summary": "",
        "input_source": "file",
        "last_uploaded_names": [],
        "chat_manager": None,
        "chat_messages": []
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
            
    if not st.session_state.summary_history:
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    st.session_state.summary_history = json.load(f)
            except:
                pass

def save_to_history(source_name: str, summary: str):
    entry = {
        "source_name": source_name,
        "summary_preview": (summary[:150] + "…") if len(summary) > 150 else summary,
        "full_summary": summary,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    st.session_state.summary_history.insert(0, entry)
    st.session_state.summary_history = st.session_state.summary_history[:50]
    
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.summary_history, f, ensure_ascii=False, indent=2)
    except:
        pass

# ---------------------------------------------------------------------------
# Data Processing Engines
# ---------------------------------------------------------------------------
def extract_text_from_pdf(file) -> str:
    """Extracts PDF text robustly using a temporary file for RapidOCRPDF."""
    temp_path = None
    try:
        # RapidOCRPDF requires a file path, safely create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.getvalue())
            temp_path = tmp.name
            
        pdf_extracter = RapidOCRPDF()
        text_per_pages = pdf_extracter(temp_path)
        data = "\n".join([str(t[1]) if isinstance(t, tuple) else str(t) for t in text_per_pages])
        return data if data.strip() else "[No readable text found in PDF]"
        
    except Exception as e:
        return f"[Error extracting PDF text: {str(e)}]"
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

def extract_text_from_file(uploaded_file) -> str:
    if uploaded_file is None: return ""
    name = (uploaded_file.name or "").lower()
    if name.endswith(".txt"):
        return uploaded_file.getvalue().decode("utf-8", errors="replace")
    elif name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    return "[Unsupported file type.]"

def translate_massive_text_ui(raw_text, target_language='en', chunk_limit=4000):
    translator = GoogleTranslator(source='auto', target=target_language)
    text_chunks = textwrap.wrap(raw_text, width=chunk_limit, replace_whitespace=False)
    translated_full_text = ""
    
    progress_bar = st.progress(0, text="Starting Translation...")
    for i, chunk in enumerate(text_chunks):
        try:
            progress_bar.progress((i + 1) / len(text_chunks), text=f"Translating chunk {i+1}/{len(text_chunks)}...")
            translated_full_text += translator.translate(chunk) + " "
        except Exception as e:
            st.warning(f"Failed to translate chunk {i + 1}. Error: {e}")
            
    progress_bar.empty()
    return translated_full_text.strip()

def summarize_in_chunks_ui(raw_text, client):
    text_chunks = textwrap.wrap(raw_text, width=40000, replace_whitespace=False)
    system_prompt = """
    You are an expert content synthesizer. Summarize the provided text.
    Focus on factual accuracy and eliminate fluff.
    Style: Use concise paragraphs. Use ASCII art or bullet points to structure.
    Do NOT be redundant.
    """
    full_summary = ""
    progress_bar = st.progress(0, text="Preparing Groq AI Summarization...")

    for i, chunk in enumerate(text_chunks):
        progress_bar.progress((i + 1) / len(text_chunks), text=f"Summarizing chunk {i+1}/{len(text_chunks)} via Llama 3.3...")
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": chunk}
                ]
            )
            chunk_summary = completion.choices[0].message.content
            full_summary += f"\n\n--- Summary of Part {i + 1} ---\n" + chunk_summary
            
            if i < len(text_chunks) - 1:
                time.sleep(1.2) # Groq rate limit safety buffer
                
        except Exception as e:
            st.error(f"Groq API Error on chunk {i + 1}: {e}")
            break
            
    progress_bar.empty()
    return full_summary

# ---------------------------------------------------------------------------
# UI Rendering
# ---------------------------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        st.markdown("### Dashboard")
        st.markdown("---")
        if not st.session_state.summary_history:
            st.markdown("""<div style='text-align:center; color:#94a3b8; padding:2rem;'>No summaries yet.</div>""", unsafe_allow_html=True)
        else:
            for i, entry in enumerate(st.session_state.summary_history):
                with st.expander(f"{entry['source_name']} - {entry['timestamp']}", expanded=False):
                    st.markdown(f"**Preview:** {entry['summary_preview']}")
                    st.text_area("Summary", entry['full_summary'], height=150, disabled=True, key=f"hist_{i}")
        
        if st.button("Clear History", use_container_width=True):
            st.session_state.summary_history = []
            if os.path.exists(HISTORY_FILE): os.remove(HISTORY_FILE)
            st.rerun()

def render_file_upload_tab():
    st.markdown('<h2 class="upload-section-heading">Upload Files</h2>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Drag and drop files here or click to browse",
        type=["pdf", "txt"], accept_multiple_files=True
    )
    
    if uploaded_files:
        current_names = sorted(f.name for f in uploaded_files)
        if st.session_state.get("last_uploaded_names") != current_names:
            combined_parts = []
            with st.spinner("Extracting text..."):
                for f in uploaded_files:
                    combined_parts.append(extract_text_from_file(f))
            st.session_state.current_extracted_text = "\n\n".join(combined_parts).strip()
            st.session_state.current_file_name = ", ".join(f.name for f in uploaded_files)
            st.session_state.last_uploaded_names = current_names
            st.session_state.input_source = "file"
        
        st.markdown('<p class="section-heading-small">Selected Files</p>', unsafe_allow_html=True)
        for f in uploaded_files:
            size_mb = len(f.getvalue()) / 1024 / 1024
            icon = "pdf" if f.name.lower().endswith('.pdf') else "txt"
            st.markdown(f"""
                <div class="file-card">
                    <span class="file-card-icon {icon}">{icon.upper()}</span>
                    <span class="file-card-name">{f.name}</span>
                    <span class="file-card-size">{size_mb:.2f} MB</span>
                </div>
            """, unsafe_allow_html=True)
            
        if st.session_state.current_extracted_text and not st.session_state.current_extracted_text.startswith("[Error"):
            with st.expander("View Extracted Text Preview"):
                preview = st.session_state.current_extracted_text[:2000]
                st.markdown(f'<div class="preview-container">{preview}...</div>', unsafe_allow_html=True)
    else:
        st.session_state.current_file_name = None
        st.session_state.current_extracted_text = ""
        st.session_state.last_uploaded_names = []

def main():
    init_session_state()
    render_sidebar()
    
    st.markdown("""
    <div class="gradient-header">
        <h1>Précis</h1>
        <p>Intelligent text condensation · Powered by Llama 3.3 · 70B</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check for API Key
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        st.error("⚠️ GROQ_API_KEY environment variable is not set. The app cannot summarize without it.")
        st.stop()
        
    groq_client = Groq(api_key=groq_api_key)
    
    tab1, tab2 = st.tabs(["Upload File", "Enter Text"])
    with tab1: render_file_upload_tab()
    with tab2:
        st.markdown('<h2 class="section-heading">Enter Text</h2>', unsafe_allow_html=True)
        manual_text = st.text_area("Content", value=st.session_state.manual_input_text, height=400)
        st.session_state.manual_input_text = manual_text
        if manual_text.strip(): st.session_state.input_source = "manual"

    current_text = st.session_state.current_extracted_text if st.session_state.input_source == "file" else st.session_state.manual_input_text
    source_name = st.session_state.current_file_name if st.session_state.input_source == "file" else "Manual Input"

    st.markdown("---")
    
    # Custom Execution Row
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        translate_toggle = st.checkbox("🌐 Translate to English before summarizing")
    with col2:
        generate_clicked = st.button("Generate Summary", type="primary", use_container_width=True)

    if generate_clicked:
        if current_text.strip() and not current_text.startswith("[Error"):
            working_text = current_text
            
            if translate_toggle:
                working_text = translate_massive_text_ui(working_text)
                
            summary_output = summarize_in_chunks_ui(working_text, groq_client)
            st.session_state.last_summary = summary_output
            save_to_history(source_name, summary_output)
            
            # Phase 2: Initialize Chat Memory automatically upon new summary
            st.session_state.chat_manager = FastContextManager(max_words=10000)
            system_instruction = f"You are an expert analytical assistant. Base all your answers strictly on this document summary:\n{summary_output}"
            st.session_state.chat_manager.add_message("system", system_instruction)
            st.session_state.chat_messages = []
            st.rerun()
        else:
            st.warning("Please provide valid text content first.")

    # Render Output & Phase 2 (Chat)
    if st.session_state.last_summary:
        st.markdown('<h2 class="section-heading">Summary Output</h2>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="summary-card">
            <div>
                <span class="stat-badge">Original Source Length: {len(current_text.split()):,} words</span>
                <span class="stat-badge">Summary Length: {len(st.session_state.last_summary.split()):,} words</span>
            </div>
            <div style="margin-top: 1.5rem; line-height: 1.8; color: #ddd8cc; white-space: pre-wrap;">
                {st.session_state.last_summary}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Interactive Chat Section
        st.markdown("---")
        st.markdown('<h2 class="section-heading-small">Interactive Document Analysis</h2>', unsafe_allow_html=True)
        
        # Display chat history
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
        # Chat input handler
        if prompt := st.chat_input("Ask a question about your document..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            with st.chat_message("assistant"):
                with st.spinner("Analyzing context..."):
                    reply = st.session_state.chat_manager.generate_response(prompt)
                    st.markdown(reply)
            st.session_state.chat_messages.append({"role": "assistant", "content": reply})

    st.markdown("""<div style="text-align:center; padding: 2rem; color: #64748b;">Précis © 2026</div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()