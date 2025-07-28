from services.document_reader import document_embedding
from fastapi import UploadFile, File
from datetime import datetime
import fitz

async def handle_document_upload(file: UploadFile = File(...)):
    print("Loading document")
    content = await file.read()
    doc = fitz.open(stream=content, filetype="pdf")
    text = ""
    
    print("PDF Read...", file.filename)
    for page in doc:
        text += page.get_text()
    
    print("Text Extracted...", text)
    # Create object with datetime as ISO format string
    file_data = {
        'text': text,
        'filename': file.filename,
        'user_id': 'hiren',
        'created_at': datetime.now().isoformat()
    }
    result = await document_embedding(file_data)
    
    return result
    
