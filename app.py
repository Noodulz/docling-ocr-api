from flask import Flask, request, Response
from docling.document_converter import DocumentConverter
import tempfile
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return "OK", 200

@app.route('/ocr', methods=['POST'])
def docling_ocr():
    """
    Extract text from PDF and return as plain markdown
    
    Usage:
    curl -X POST -F "file=@document.pdf" http://your-url/ocr
    
    Returns: Plain markdown text
    """
    try:
        # Get PDF from request
        if 'file' in request.files:
            pdf_file = request.files['file']
            pdf_bytes = pdf_file.read()
        else:
            # If sent as raw body
            pdf_bytes = request.data
        
        if not pdf_bytes:
            return "Error: No PDF data received", 400
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            temp_pdf.write(pdf_bytes)
            temp_path = temp_pdf.name
        
        try:
            # Convert PDF to markdown using Docling
            converter = DocumentConverter()
            result = converter.convert(source=temp_path)
            markdown_text = result.document.export_to_markdown()
            
            # Return as plain text
            return Response(markdown_text, mimetype='text/plain')
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        return f"Error processing PDF: {str(e)}", 500

if __name__ == '__main__':
    # Port is set by Code Engine via environment variable
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
