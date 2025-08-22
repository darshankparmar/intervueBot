"""
File upload endpoints for IntervueBot API.

This module handles file uploads including resumes, CVs, and cover letters.
Files are stored and managed separately from interview sessions.
"""

import logging
import uuid
from typing import List
import fitz  # PyMuPDF
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

from ....schemas.file import FileUploadResponse, FileInfo
from ....services.file_upload_service import file_upload_service
from ....core.config import settings
from ....agents.resume_parser_agent import ResumeParserAgent

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload",
    response_model=FileUploadResponse,
    summary="Upload Files",
    description="""
    Upload files (resumes, CVs, cover letters) for interview preparation.
    
    This endpoint:
    1. Accepts file uploads
    2. Stores files securely
    3. Returns unique file identifiers
    4. Supports multiple file formats (PDF, DOC, DOCX, TXT, RTF)
    
    ## File Requirements:
    - Maximum 10MB per file
    - Supported formats: PDF, DOC, DOCX, TXT, RTF
    - Files are stored with unique identifiers
    
    ## Response:
    - File IDs for use in interview start
    - File metadata (name, type, size)
    - Upload status and any errors
    """,
    response_description="File upload results with unique identifiers",
    tags=["Files"],
    responses={
        200: {
            "description": "Files uploaded successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Files uploaded successfully",
                        "files": [
                            {
                                "file_id": "file_123456789",
                                "filename": "resume.pdf",
                                "file_type": "resume",
                                "size": 1024000,
                                "uploaded_at": "2024-01-15T10:30:00Z"
                            }
                        ]
                    }
                }
            }
        },
        400: {
            "description": "Invalid file or upload error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "File too large or unsupported format"
                    }
                }
            }
        }
    })
async def upload_files(
    files: List[UploadFile] = File(..., description="Files to upload")
) -> FileUploadResponse:
    """
    Upload files for interview preparation.
    
    Args:
        files: List of files to upload
        
    Returns:
        FileUploadResponse: Upload results with file identifiers
        
    Raises:
        HTTPException: If upload fails
    """
    try:
        if not files:
            raise HTTPException(
                status_code=400,
                detail="No files provided"
            )
        
        logger.info(f"Processing {len(files)} file uploads")
        
        uploaded_files = []
        errors = []
        
        for file in files:
            try:
                # Validate file size (10MB limit)
                if file.size > 10 * 1024 * 1024:  # 10MB
                    errors.append(f"File {file.filename} is too large (max 10MB)")
                    continue
                
                # Validate file type
                allowed_extensions = {'.pdf', '.doc', '.docx', '.txt', '.rtf'}
                file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
                if f'.{file_extension}' not in allowed_extensions:
                    errors.append(f"File {file.filename} has unsupported format")
                    continue
                
                # Generate unique file ID
                file_id = f"file_{uuid.uuid4().hex[:12]}"
                
                # Store file content
                file_content = await file.read()
                
                doc = fitz.open(stream=file_content, filetype="pdf")
                file_text = ""
                for page in doc:
                    file_text += page.get_text()
                
                # Parse resume
                print("file_text : ", file_text)
                resume_parser_agent = ResumeParserAgent()
                json_template = {
                    "name": "string",
                    "email": "user@example.com",
                    "position": "string",
                    "experience_level": "junior",
                    "interview_type": "technical"
                }
                resume_data = resume_parser_agent.extract_data_from_pdf(file_text, json_template)
                
                print("resume_data : ", resume_data)
                # Store file using file upload service
                stored_file = await file_upload_service.store_file(
                    file_id=file_id,
                    filename=file.filename,
                    file_type="resume",  # Default type, can be enhanced later
                    content=file_content
                )
                
                # Create file info
                file_info = FileInfo(
                    file_id=file_id,
                    filename=file.filename,
                    file_type="resume",
                    size=file.size,
                    uploaded_at=stored_file.uploaded_at
                )
                
                uploaded_files.append(file_info)
                logger.info(f"Successfully uploaded file: {file_id} ({file.filename})")
                
            except Exception as e:
                logger.error(f"Failed to upload file {file.filename}: {e}")
                errors.append(f"Failed to upload {file.filename}: {str(e)}")
        
        if not uploaded_files:
            raise HTTPException(
                status_code=400,
                detail=f"No files were uploaded successfully. Errors: {'; '.join(errors)}"
            )
        
        # Prepare response
        status = "success" if not errors else "partial_success"
        message = "Files uploaded successfully" if not errors else f"Some files uploaded with errors: {'; '.join(errors)}"
        
        return FileUploadResponse(
            status=status,
            message=message,
            files=uploaded_files,
            errors=errors if errors else [],
            resume_data=resume_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"File upload failed: {str(e)}"
        )


@router.get("/{file_id}",
    summary="Get File Info",
    description="Get information about an uploaded file",
    response_description="File information",
    tags=["Files"])
async def get_file_info(file_id: str):
    """Get file information by ID."""
    try:
        file_info = await file_upload_service.get_file_info(file_id)
        if not file_info:
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        return file_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get file info: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get file info: {str(e)}"
        )


@router.delete("/{file_id}",
    summary="Delete File",
    description="Delete an uploaded file",
    response_description="File deletion result",
    tags=["Files"])
async def delete_file(file_id: str):
    """Delete a file by ID."""
    try:
        success = await file_upload_service.delete_file(file_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        return {"status": "success", "message": "File deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete file: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        ) 