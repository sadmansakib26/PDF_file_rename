import os
import PyPDF2
import re
import google.generativeai as genai
import streamlit as st
import zipfile
import io
from dotenv import load_dotenv
import time
import concurrent.futures

load_dotenv()

api_key = os.getenv("GENAI_API_KEY")

if api_key is None:
    st.error("Missing environment variable: GENAI_API_KEY")
    st.stop()

genai.configure(api_key=api_key)

# Set up the model
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 200,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

system_instruction = """Input: The first page of a scientific journal article.
            Output: Reply with the title of the paper followed by the last name of the first author
            followed by the year. Format the response as: "Title of the Paper - First Author's Last Name - Year".
            Do not include any additional text or information."""

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

@st.cache_data
def process_pdf(pdf_file):
    try:
        pdf_bytes = pdf_file.read()
        pdf_io = io.BytesIO(pdf_bytes)
        reader = PyPDF2.PdfReader(pdf_io)
        content = reader.pages[0].extract_text()
        lines = content.split("\n")
        first_50_lines = lines[:50]
        clean_lines = [re.sub(r"\W+", " ", line) for line in first_50_lines]
        message = " ".join(clean_lines)
        response = model.generate_content([system_instruction, message])
        clean_filename = re.sub(r'[\\/:*?"<>|]', "", response.text).strip() + ".pdf"
        return clean_filename, pdf_bytes
    except Exception as e:
        return f"Error processing {pdf_file.name}: {str(e)}", None

def process_pdfs_concurrently(pdf_files):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        return list(executor.map(process_pdf, pdf_files))

st.set_page_config(page_title="Scientific Paper PDF Renamer", page_icon="📄", layout="wide")

# Initialize session state
if 'upload_key' not in st.session_state:
    st.session_state.upload_key = 0

def reset_upload():
    st.session_state.upload_key += 1
    st.experimental_rerun()

st.title("Scientific Paper PDF File Rename")
st.write("Automatically rename PDF files of scientific papers based on their title using Google Gemini AI")

uploaded_files = st.file_uploader("Choose PDF files", accept_multiple_files=True, type="pdf", key=f"uploader_{st.session_state.upload_key}")

if uploaded_files:
    st.write(f"Uploaded {len(uploaded_files)} file(s)")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Rename Files"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            results = process_pdfs_concurrently(uploaded_files)

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for i, (new_filename, pdf_content) in enumerate(results):
                    if pdf_content is not None:
                        zip_file.writestr(new_filename, pdf_content)
                        status_text.text(f"Processed: {uploaded_files[i].name} -> {new_filename}")
                    else:
                        st.error(new_filename)  # Display error message
                    progress_bar.progress((i + 1) / len(uploaded_files))
                    time.sleep(0.1)  # Small delay to avoid rate limiting

            zip_buffer.seek(0)
            st.download_button(
                label="Download Renamed PDFs",
                data=zip_buffer,
                file_name="renamed_pdfs.zip",
                mime="application/zip"
            )
            st.success("All files renamed and ready for download!")

    with col2:
        if st.button("Upload Again"):
            reset_upload()

st.sidebar.title("About")
st.sidebar.info(
    "This app uses Google's Gemini AI to rename scientific paper PDFs based on their content. "
    "Upload your PDFs, click 'Rename Files', and download the zip file with renamed PDFs."
)