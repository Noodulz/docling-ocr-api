from flask import Flask, request, Response
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
import tempfile
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

@app.route('/ocr', methods=['POST'])
def convert_pdf():
    """
    Convert PDF to markdown using Tesseract OCR
    """
    try:
        if 'file' in request.files:
            pdf_file = request.files['file']
            pdf_bytes = pdf_file.read()
        else:
            pdf_bytes = request.data
        
        if not pdf_bytes:
            return "Error: No PDF provided", 400
        
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
            
            return Response(markdown, mimetype='text/plain')
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
