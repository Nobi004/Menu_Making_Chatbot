import streamlit as st 
from extract_text import extract_text 
uploaded_file = st.file_uploader("Upload your file", type=["pdf","png","jpg","jpeg","docx","txt"])


if uploaded_file is not None:
    extracted_text = extract_text(uploaded_file,filename=uploaded_file.name)
    st.text_area("Extracted Text",extracted_text,height=300)