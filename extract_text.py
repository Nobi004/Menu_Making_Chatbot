import fitz 
import pytesseract 
from PIL import Image
from io import BytesIO
import docx 
import os 

# Extracting text from .txt file
def extract_text_from_text(file_bytes):        
    return file_bytes.decode("utf-8").strip()

# Extract text from .docx file
def extract_text_from_docx(file_bytes):
    with BytesIO(file_bytes) as f:
        doc = docx.Document(f)
        full_text= []
        for para in doc.paragraphs:
            full_text.append(para.text)
            
        return "\n".join(full_text).strip()

# Extract text from image file    
def extract_text_from_image(file_bytes):
    img = Image.open(BytesIO(file_bytes))
    text = pytesseract.image_to_string(img,lang="eng")
    return text.strip()

# Extract text from pdf documents
def extract_text_from_pdf(file_bytes):
    text = ""
    doc = fitz.open(stream=file_bytes,filetype="pdf")
    
    # text based pdf
    for page in doc:
        page_text = page.get_text()
        if page_text.strip():
            text += page_text + "\n"
            
    # Scanned pdf/ img based pdf
    if not text.strip():
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB",[pix.weight,pix.height],pix.samples)
            ocr_text = pytesseract.image_to_string(img,lang="eng","duetsch")
            text += ocr_text + "\n"
    return text.strip()


def extract_text(file,filename=None):
    # Read bytes (if file is BytesIO or stream)
    if hasattr(file,"read"):
        file_bytes = file.read()
        
        # Reset stream position for safety (for reuse later)
        if hasattr(file,"seek"):
            file.seek(0)
    elif isinstance(file,bytes):
        file_bytes =file
    else:
        raise ValueError("Input file must be a file-like object or bytes")
    
    # Detect Extension
    ext = None
    if filename:
        ext = os.path.splitext(filename)[1].lower()
    elif hasattr(file,"name"):
        ext = os.path.splitext(file.name)[1].lower()
        
    # Heuristic based on extension or fallback on MIME/type if available
    if ext in [".pdf"]:
        return extract_text_from_pdf(file_bytes)
    elif ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
        return extract_text_from_image(file_bytes)
    elif ext in [".docx"]:
        return extract_text_from_docx(file_bytes)
    elif ext in [".txt"]:
        return extract_text_from_text(file_bytes)
    else:
        # Try PDF extraction as fallback for unknown types
        try:
            return extract_text_from_pdf(file_bytes)
        except Exception:
            try: 
                return extract_text_from_image(file_bytes)
            except Exception:
                return  "" # Could not extract text
                        