# routes/document_routes.py
from fastapi import APIRouter, UploadFile, File
from controllers.document_controller import handle_document_upload

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):    
    return await handle_document_upload(file)
