# Menu Making Chatbot 🤖

> An AI-powered menu processing application that converts restaurant menus into structured data using OpenAI's GPT model.

## 🚀 Features

### File Support
- 📄 PDF documents
- 🖼️ Images (PNG, JPG, JPEG, BMP)
- 📝 Word documents (DOCX)
- 📰 Text files (TXT)

### Processing Capabilities
- 🤖 AI-powered menu item extraction
- 💰 Automatic price detection
- 🌍 Multi-language support (English/German)
- 🔤 Special character handling
- 📊 Structured data output

### Export Options
- 📊 CSV format for POS systems
- 📄 PDF documents
- 📝 Word documents

## 📋 Prerequisites

- Python 3.8 or higher
- Tesseract OCR ([Download Link](https://github.com/UB-Mannheim/tesseract/wiki))
- OpenAI API key

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/Menu_Making_Chatbot.git
cd Menu_Making_Chatbot
```

2. **Set up virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
Create a `.env` file in the project root:
```plaintext
API=your_openai_api_key_here
```

## 📦 Dependencies

```plaintext
streamlit>=1.24.0
pandas>=1.5.3
python-docx>=0.8.11
Pillow>=9.5.0
fpdf>=1.7.2
python-dotenv>=1.0.0
PyMuPDF>=1.22.3
pytesseract>=0.3.10
openai>=0.27.8
```

## 🚀 Usage

1. **Start the application**
```bash
streamlit run app.py
```

2. **Upload your menu**
   - Drag and drop your menu file
   - Supported formats: PDF, Images, DOCX, TXT

3. **Review and Edit**
   - Check extracted menu items
   - Edit prices and categories
   - Add missing items

4. **Export**
   - Download as CSV for POS systems
   - Generate PDF document
   - Create Word document

## 📁 Project Structure

```plaintext
Menu_Making_Chatbot/
├── app.py              # Streamlit web application
├── extract_text.py     # Text extraction module
├── menu_processor.py   # Menu processing logic
├── llm_clients/        # LLM API clients
│   ├── __init__.py
│   ├── factory.py
│   └── openai_client.py
├── .env               # Environment variables
└── requirements.txt   # Project dependencies
```

## ⚠️ Troubleshooting

### Common Issues and Solutions

1. **Tesseract OCR Error**
   - Verify Tesseract is installed
   - Check PATH environment variable
   - Default path: `C:\Program Files\Tesseract-OCR\tesseract.exe`

2. **OpenAI API Issues**
   - Verify API key in `.env`
   - Check internet connection
   - Monitor API rate limits

3. **PDF Processing**
   - Install all PyMuPDF dependencies
   - Check PDF file permissions
   - Try converting to image if persistent issues

4. **Memory Issues**
   - Reduce file size if possible
   - Close other applications
   - Check available system memory

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- Your Name - *Initial work* - [YourGithub](https://github.com/yourusername)

## 🙏 Acknowledgments

- OpenAI for GPT API
- Streamlit team for the framework
- Tesseract OCR project