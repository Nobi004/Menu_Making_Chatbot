import streamlit as st
import pandas as pd
import tempfile
import os
from io import BytesIO
from menu_processor import MenuProcessor
from extract_text import extract_text
from dotenv import load_dotenv
from docx import Document
from fpdf import FPDF
from PIL import Image

load_dotenv()
OPENAI_API_KEY = os.getenv("API")

st.set_page_config(page_title="Menu Processor", layout="wide")
st.title("📋 AI Menu Card Processor")

lang = st.radio("🌐 Select Language / Sprache wählen", ["English", "German"])
labels = {
    "English": {
        "upload": "Upload your menu file (PDF, Image, DOCX, etc.)",
        "processing": "Processing file...",
        "download": "Download as",
        "csv": "CSV",
        "pdf": "PDF",
        "docx": "Word Doc",
        "error": "❌ Error:",
        "no_preview": "No preview available for this file type.",
    },
    "German": {
        "upload": "Lade deine Menüdatei hoch (PDF, Bild, DOCX usw.)",
        "processing": "Datei wird verarbeitet...",
        "download": "Herunterladen als",
        "csv": "CSV",
        "pdf": "PDF",
        "docx": "Word-Dokument",
        "error": "❌ Fehler:",
        "no_preview": "Für diesen Dateityp ist keine Vorschau verfügbar.",
    }
}[lang]

uploaded_file = st.file_uploader(labels["upload"], type=["pdf", "png", "jpg", "jpeg", "bmp", "heic", "docx", "txt"])

processor = MenuProcessor(llm_provider="openai", api_key=OPENAI_API_KEY)

def show_file_preview(file_bytes: bytes, filename: str):
    ext = os.path.splitext(filename)[1].lower()

    if ext in [".png", ".jpg", ".jpeg", ".bmp", ".heic"]:
        # Display image from bytes
        try:
            img = Image.open(BytesIO(file_bytes))
            st.image(img)
        except Exception as e:
            st.write(f"Error displaying image preview: {e}")

    elif ext == ".pdf":
        # Save to temp file and show iframe
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file_bytes)
            tmp_file.flush()
            pdf_path = tmp_file.name
        # Display PDF in iframe
        st.markdown(f'<iframe src="file://{pdf_path}" width="100%" height="600px"></iframe>', unsafe_allow_html=True)

    elif ext == ".docx":
        # Extract text and show in text_area
        try:
            text = extract_text(file_bytes, filename=filename)
            st.text_area("Document text preview", text, height=600)
        except Exception as e:
            st.write(f"Error displaying DOCX preview: {e}")

    elif ext == ".txt":
        try:
            text = file_bytes.decode("utf-8")
            st.text_area("Text file preview", text, height=600)
        except Exception as e:
            st.write(f"Error displaying TXT preview: {e}")

    else:
        st.write(labels["no_preview"])


if uploaded_file:
    with st.spinner(labels["processing"]):
        try:
            file_bytes = uploaded_file.read()  # read bytes once

            # process menu items
            items = processor.process_menu_file(BytesIO(file_bytes), filename=uploaded_file.name)

            df = pd.DataFrame(items)

            left_col, right_col = st.columns([3, 2])

            with left_col:
                edited_df = st.data_editor(df, num_rows="dynamic", key="menu_editor")

                csv_string = processor.generate_csv(edited_df.to_dict(orient="records"), "items_empty.csv")

                def download_pdf(df):
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=10)
                    for i, row in df.iterrows():
                        line = ", ".join(f"{col}: {row[col]}" for col in df.columns)
                        pdf.cell(200, 10, txt=line, ln=1)
                    buffer = BytesIO()
                    pdf.output(buffer)
                    return buffer.getvalue()

                def download_docx(df):
                    doc = Document()
                    for i, row in df.iterrows():
                        line = ", ".join(f"{col}: {row[col]}" for col in df.columns)
                        doc.add_paragraph(line)
                    buffer = BytesIO()
                    doc.save(buffer)
                    return buffer.getvalue()

                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(labels["csv"], data=csv_string, file_name="menu.csv", mime="text/csv")
                with col2:
                    docx_data = download_docx(edited_df)
                    pdf_data = download_pdf(edited_df)
                    st.download_button(labels["docx"], data=docx_data, file_name="menu.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    st.download_button(labels["pdf"], data=pdf_data, file_name="menu.pdf", mime="application/pdf")

            with right_col:
                st.header("Original File Preview")
                show_file_preview(file_bytes, uploaded_file.name)

        except Exception as e:
            st.error(f"{labels['error']} {str(e)}")
