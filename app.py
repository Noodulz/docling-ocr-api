from flask import Flask, request, Response, jsonify
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
import tempfile
import os
import base64

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

@app.route('/ocr', methods=['POST'])
def convert_pdf():
    """
    Convert PDF to markdown using Tesseract OCR
    Supports multiple input formats for WxO compatibility
    """
    try:
        pdf_bytes = None
        
        # Method 1: multipart/form-data (for curl testing)
        if 'file' in request.files:
            pdf_file = request.files['file']
            pdf_bytes = pdf_file.read()
        
        # Method 2: JSON with base64 (for WxO)
        elif request.is_json:
            data = request.get_json()
            if 'file' in data:
                try:
                    pdf_bytes = base64.b64decode(data['file'])
                except Exception:
                    # If it's not base64, treat as raw
                    pdf_bytes = data['file'].encode() if isinstance(data['file'], str) else data['file']
        
        # Method 3: Raw binary (for WxO direct binary)
        elif request.data:
            pdf_bytes = request.data
        
        if not pdf_bytes:
            return jsonify({"error": "No PDF provided"}), 400
        
        # Validate it's a PDF
        if not pdf_bytes.startswith(b'%PDF'):
            return jsonify({"error": "Invalid PDF file"}), 400
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            temp_pdf.write(pdf_bytes)
            temp_path = temp_pdf.name
        
        try:
            # Force Tesseract by setting environment variable
            os.environ['DOCLING_OCR_ENGINE'] = 'tesseractcli'
            
            # Enable OCR with default settings (will use Tesseract)
            pipeline_options = PdfPipelineOptions()
            pipeline_options.do_ocr = True
            pipeline_options.do_table_structure = True
            pipeline_options.table_structure_options.do_cell_matching = True
            pipeline_options.ocr_options.lang = ["en"]
            pipeline_options.accelerator_options = AcceleratorOptions(
                num_threads=4, device=AcceleratorDevice.AUTO
            )
            
            converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                }
            )
            
            result = converter.convert(temp_path)
            markdown = result.document.export_to_markdown()
            
            # Return plain text for compatibility
            return Response(markdown, mimetype='text/plain')
        
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
