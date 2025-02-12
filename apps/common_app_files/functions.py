from streamlit.web.server.websocket_headers import _get_websocket_headers
#import streamlit as st
from docx import Document
from pdfminer.high_level import extract_text

def get_logged_in_user():
    headers = _get_websocket_headers()
    #headers = st.context.headers
    user_name = headers.get("Sf-Context-Current-User", "Unknown")
    return user_name

def process_docx_file(docx_file) -> str:
    document = Document(docx_file)
    text = []
    for paragraph in document.paragraphs:
        text.append(paragraph.text)
    return "\n".join(text)

def process_pdf_file(uploaded_file):
    try:
        text = extract_text(uploaded_file)
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return "Error reading PDF file."
    
def check_file_exceptions(uploaded_files):
    if uploaded_files is None or len(uploaded_files) < 2:
        return False, "Please upload more than one file to proceed."
    
    file_names = [file.name for file in uploaded_files]
    
    if len(file_names) != len(set(file_names)):
        return False, "You have uploaded the same file more than once. Please remove the duplicates."
    
    return True, None
