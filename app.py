import streamlit as st
import pandas as pd
import tempfile
import os
import base64
from io import BytesIO
from menu_processor import MenuProcessor
from extract_text import extract_text
from dotenv import load_dotenv
from docx import Document
from fpdf import FPDF
from PIL import Image

# Try to import PyMuPDF, but don't fail if not available
try:
    import fitz  # PyMuPDF for PDF preview
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

load_dotenv()
OPENAI_API_KEY = os.getenv("API")

st.set_page_config(page_title="Menu Processor", layout="wide")
st.title("📋 AI Menu Card Processor")

# Language selection
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
        "original_file": "Original File Preview",
        "editable_data": "Editable Menu Data",
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
        "original_file": "Originaldatei-Vorschau",
        "editable_data": "Bearbeitbare Menüdaten",
    }
}[lang]

# File uploader
uploaded_file = st.file_uploader(
    labels["upload"], 
    type=["pdf", "png", "jpg", "jpeg", "bmp", "heic", "docx", "txt"]
)

# Initialize processor
processor = MenuProcessor(llm_provider="openai", api_key=OPENAI_API_KEY)

def show_file_preview(file_bytes: bytes, filename: str):
    """Enhanced file preview function with better error handling"""
    if not file_bytes:
        st.error("No file data available for preview")
        return
        
    ext = os.path.splitext(filename)[1].lower()
    
    try:
        if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
            img = Image.open(BytesIO(file_bytes))
            st.image(img, use_column_width=True)
        
        elif ext == ".heic":
            st.info("HEIC files may not display properly. Consider converting to JPG.")
            try:
                img = Image.open(BytesIO(file_bytes))
                st.image(img, use_column_width=True)
            except:
                st.error("Cannot display HEIC file")

        elif ext == ".pdf":
            if PYMUPDF_AVAILABLE:
                try:
                    # Use PyMuPDF for better PDF preview
                    doc = fitz.open(stream=file_bytes, filetype="pdf")
                    for page_num in range(min(3, len(doc))):  # Show first 3 pages max
                        page = doc.load_page(page_num)
                        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))  # Higher resolution
                        img_data = pix.tobytes("png")
                        st.image(img_data, caption=f"Page {page_num + 1}", use_column_width=True)
                    
                    if len(doc) > 3:
                        st.info(f"Showing first 3 pages of {len(doc)} total pages")
                    doc.close()
                except Exception as e:
                    st.error(f"Error displaying PDF with PyMuPDF: {str(e)}")
            else:
                # Fallback PDF preview using base64 embedding
                try:
                    base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
                    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf">'
                    st.markdown(pdf_display, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error displaying PDF: {str(e)}")

        elif ext == ".docx":
            try:
                # Try to extract text for preview using python-docx
                doc = Document(BytesIO(file_bytes))
                text_content = []
                for paragraph in doc.paragraphs[:20]:  # First 20 paragraphs
                    if paragraph.text.strip():
                        text_content.append(paragraph.text)
                
                preview_text = '\n\n'.join(text_content)
                if preview_text:
                    st.text_area("Document Preview", preview_text, height=400, key=f"docx_preview_{hash(filename)}")
                else:
                    st.info("Document appears to be empty or contains only images/tables")
                    
                if len(doc.paragraphs) > 20:
                    st.info(f"Showing first 20 paragraphs of {len(doc.paragraphs)} total")
                    
            except Exception as e:
                # Fallback to extract_text function
                try:
                    text = extract_text(file_bytes, filename=filename)
                    st.text_area("Document Preview", text, height=400, key=f"docx_fallback_{hash(filename)}")
                except Exception as e2:
                    st.error(f"Error displaying DOCX: {str(e2)}")

        elif ext == ".txt":
            try:
                text = file_bytes.decode("utf-8")
                # Limit preview to first 5000 characters
                if len(text) > 5000:
                    preview_text = text[:5000] + "\n\n... (truncated)"
                    st.info("Showing first 5000 characters")
                else:
                    preview_text = text
                st.text_area("Text File Preview", preview_text, height=400, key=f"txt_preview_{hash(filename)}")
            except UnicodeDecodeError:
                try:
                    text = file_bytes.decode("latin-1")
                    st.text_area("Text File Preview", text[:5000], height=400, key=f"txt_preview_latin_{hash(filename)}")
                except Exception as e:
                    st.error(f"Error decoding text file: {str(e)}")
        else:
            st.info(labels["no_preview"])
            
    except Exception as e:
        st.error(f"Error displaying file: {str(e)}")
        st.info("File uploaded successfully but preview unavailable")

def download_pdf(df):
    """Generate PDF from DataFrame"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    # Add title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Menu Items", ln=1, align='C')
    pdf.ln(10)
    
    # Add data
    pdf.set_font("Arial", size=10)
    for i, row in df.iterrows():
        line = ", ".join(f"{col}: {str(row[col])}" for col in df.columns if pd.notna(row[col]))
        # Handle long lines by splitting
        if len(line) > 80:
            words = line.split(', ')
            current_line = ""
            for word in words:
                if len(current_line + word) < 80:
                    current_line += word + ", "
                else:
                    pdf.cell(0, 8, current_line.rstrip(", "), ln=1)
                    current_line = word + ", "
            if current_line:
                pdf.cell(0, 8, current_line.rstrip(", "), ln=1)
        else:
            pdf.cell(0, 8, line, ln=1)
        pdf.ln(2)
    
    buffer = BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()

def download_docx(df):
    """Generate DOCX from DataFrame"""
    doc = Document()
    doc.add_heading('Menu Items', 0)
    
    for i, row in df.iterrows():
        line = ", ".join(f"{col}: {str(row[col])}" for col in df.columns if pd.notna(row[col]))
        doc.add_paragraph(line)
    
    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

# Main UI Logic
if uploaded_file:
    # Create two columns: left for data editor, right for file preview
    left_col, right_col = st.columns([3, 2])
    
    with st.spinner(labels["processing"]):
        try:
            # Read file bytes once and store
            uploaded_file.seek(0)  # Reset file pointer
            file_bytes = uploaded_file.read()
            
            # Try different approaches based on what your processor expects
            items = None
            error_messages = []
            
            # Try BytesIO first (most common)
            try:
                items = processor.process_menu_file(BytesIO(file_bytes), filename=uploaded_file.name)
            except Exception as e1:
                error_messages.append(f"BytesIO approach: {str(e1)}")
                
                # Try with raw bytes
                try:
                    items = processor.process_menu_file(file_bytes, filename=uploaded_file.name)
                except Exception as e2:
                    error_messages.append(f"Raw bytes approach: {str(e2)}")
                    
                    # Try with the uploaded file object directly
                    try:
                        uploaded_file.seek(0)
                        items = processor.process_menu_file(uploaded_file, filename=uploaded_file.name)
                    except Exception as e3:
                        error_messages.append(f"File object approach: {str(e3)}")
                        
                        # Last resort: create temporary file
                        try:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                                tmp_file.write(file_bytes)
                                tmp_file.flush()
                                temp_file_path = tmp_file.name
                            
                            try:
                                items = processor.process_menu_file(temp_file_path, filename=uploaded_file.name)
                            finally:
                                if os.path.exists(temp_file_path):
                                    os.unlink(temp_file_path)
                        except Exception as e4:
                            error_messages.append(f"Temp file approach: {str(e4)}")
            
            if items is None:
                st.error("Failed to process file with all approaches:")
                for i, err_msg in enumerate(error_messages, 1):
                    st.error(f"{i}. {err_msg}")
                st.stop()
            
            df = pd.DataFrame(items)
            
            # Left column: Editable data and downloads
            with left_col:
                st.header(labels["editable_data"])
                
                # Show editable dataframe
                edited_df = st.data_editor(
                    df, 
                    num_rows="dynamic", 
                    key="menu_editor",
                    use_container_width=True
                )
                
                st.subheader(labels["download"])
                
                # Generate download data
                try:
                    csv_string = processor.generate_csv(edited_df.to_dict(orient="records"), "items_empty.csv")
                except Exception as e:
                    # Fallback CSV generation if processor method fails
                    csv_string = edited_df.to_csv(index=False)
                    st.warning("Using fallback CSV generation")
                
                docx_data = download_docx(edited_df)
                pdf_data = download_pdf(edited_df)
                
                # Download buttons in a row
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button(
                        labels["csv"], 
                        data=csv_string, 
                        file_name="menu.csv", 
                        mime="text/csv",
                        use_container_width=True
                    )
                with col2:
                    st.download_button(
                        labels["docx"], 
                        data=docx_data, 
                        file_name="menu.docx", 
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
                with col3:
                    st.download_button(
                        labels["pdf"], 
                        data=pdf_data, 
                        file_name="menu.pdf", 
                        mime="application/pdf",
                        use_container_width=True
                    )
            
            # Right column: File preview
            with right_col:
                st.header(labels["original_file"])
                if file_bytes:
                    show_file_preview(file_bytes, uploaded_file.name)
                else:
                    st.error("Could not load file for preview")
                
        except Exception as e:
            st.error(f"{labels['error']} {str(e)}")
            st.write("Please check if all required modules are installed and API key is configured correctly.")
            # Show debug info
            with st.expander("Debug Information"):
                st.write(f"File name: {uploaded_file.name}")
                st.write(f"File size: {len(file_bytes) if 'file_bytes' in locals() else 'Unknown'} bytes")
                st.write(f"File type: {uploaded_file.type}")

else:
    # Show placeholder when no file is uploaded
    st.info("👆 Please upload a menu file to get started")
    
    # Optional: Show example layout
    col1, col2 = st.columns([3, 2])
    with col1:
        st.subheader("📊 Editable Data (Left Side)")
        st.write("Your processed menu data will appear here as an editable table")
        st.write("Features:")
        st.write("• Edit data directly in the table")
        st.write("• Add or remove rows")
        st.write("• Download as CSV, PDF, or Word document")
    with col2:
        st.subheader("📄 File Preview (Right Side)")
        st.write("Your uploaded file preview will appear here")
        st.write("Supported formats:")
        st.write("• PDF files (with page preview)")
        st.write("• Images (PNG, JPG, JPEG, BMP)")
        st.write("• Word documents (DOCX)")
        st.write("• Text files (TXT)")

# Optional: Add footer with instructions
st.markdown("---")
st.markdown("""
### 📝 Instructions:
1. **Upload** your menu file using the file uploader above
2. **Review** the extracted data in the left column - you can edit it directly
3. **Preview** your original file in the right column to verify accuracy
4. **Download** the processed data in your preferred format (CSV, PDF, or Word)

### 🔧 Troubleshooting:
- Make sure your OpenAI API key is properly configured
- Ensure all required Python packages are installed
- For best results, use clear, high-quality menu images or PDFs
""")