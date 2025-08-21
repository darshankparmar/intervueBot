"""
File upload endpoints for IntervueBot API.

This module handles file upload endpoints for resumes, CVs, and cover letters.
"""

import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel

from intervuebot.services.file_upload_service import file_upload_service
from intervuebot.schemas.interview import ResumeFile

logger = logging.getLogger(__name__)

router = APIRouter()


class FileUploadRequest(BaseModel):
    """Request model for file upload."""
    
    files: List[Dict[str, Any]] = []
    session_id: str = ""


class FileUploadResponse(BaseModel):
    """Response model for file upload."""
    
    success: bool
    message: str
    uploaded_files: List[ResumeFile] = []
    metadata: Dict[str, Any] = {}


@router.post("/upload",
    response_model=FileUploadResponse,
    summary="Upload Files",
    description="""
    Upload resume, CV, and cover letter files for interview processing.
    
    This endpoint accepts multiple files and processes them for:
    - File validation and type checking
    - File storage and organization
    - File URL generation
    - Metadata extraction
    
    ## Supported File Types:
    - **Resume**: PDF, DOC, DOCX, TXT, RTF
    - **CV**: PDF, DOC, DOCX, TXT, RTF  
    - **Cover Letter**: PDF, DOC, DOCX, TXT, RTF
    
    ## File Size Limits:
    - Maximum file size: 10MB per file
    - Maximum total files: 10 files per upload
    
    ## File Organization:
    - Files are stored in organized directories
    - Unique filenames are generated to prevent conflicts
    - File URLs are generated for easy access
    """,
    response_description="File upload result with processed file information",
    tags=["Uploads"],
    responses={
        200: {
            "description": "Files uploaded successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Files uploaded successfully",
                        "uploaded_files": [
                            {
                                "filename": "john_doe_resume.pdf",
                                "file_url": "/uploads/resumes/550e8400-e29b-41d4-a716-446655440000.pdf",
                                "file_type": "resume"
                            }
                        ],
                        "metadata": {
                            "total_files": 1,
                            "file_types": {"resume": 1},
                            "supported_files": 1,
                            "unsupported_files": 0
                        }
                    }
                }
            }
        },
        400: {
            "description": "Invalid file data or validation error",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "File validation failed: Unsupported file type",
                        "uploaded_files": [],
                        "metadata": {}
                    }
                }
            }
        },
        413: {
            "description": "File too large",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "File too large: Maximum size is 10MB",
                        "uploaded_files": [],
                        "metadata": {}
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "File upload failed: Internal server error",
                        "uploaded_files": [],
                        "metadata": {}
                    }
                }
            }
        }
    })
async def upload_files(request: FileUploadRequest) -> FileUploadResponse:
    """
    Upload multiple files for interview processing.
    
    This endpoint processes uploaded files and returns file information
    that can be used in the interview creation process.
    
    Args:
        request: File upload request with file data
        
    Returns:
        FileUploadResponse: Upload result with file information
        
    Raises:
        HTTPException: If upload fails or validation errors occur
    """
    try:
        logger.info(f"Processing file upload request with {len(request.files)} files")
        
        if not request.files:
            raise HTTPException(
                status_code=400,
                detail="No files provided"
            )
        
        if len(request.files) > 10:
            raise HTTPException(
                status_code=400,
                detail="Too many files: Maximum 10 files allowed"
            )
        
        # Process uploaded files
        uploaded_files = await file_upload_service.upload_files(request.files)
        
        if not uploaded_files:
            raise HTTPException(
                status_code=400,
                detail="No files were successfully processed"
            )
        
        # Get file metadata
        metadata = file_upload_service.get_file_metadata(uploaded_files)
        
        logger.info(f"Successfully uploaded {len(uploaded_files)} files")
        
        return FileUploadResponse(
            success=True,
            message=f"Successfully uploaded {len(uploaded_files)} files",
            uploaded_files=uploaded_files,
            metadata=metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"File upload failed: {str(e)}"
        )


@router.get("/files/{file_type}/{filename}",
    summary="Download File",
    description="""
    Download a specific uploaded file.
    
    This endpoint allows downloading of uploaded files by their
    filename and type for verification or processing.
    
    ## File Types:
    - **resume**: Resume files
    - **cv**: CV files  
    - **cover_letter**: Cover letter files
    
    ## Security:
    - Files are served with proper content-type headers
    - Access is restricted to uploaded files only
    - No directory traversal allowed
    """,
    response_description="File content",
    tags=["Uploads"],
    responses={
        200: {
            "description": "File content",
            "content": {
                "application/pdf": {},
                "application/msword": {},
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {},
                "text/plain": {},
                "application/rtf": {}
            }
        },
        404: {
            "description": "File not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "File not found"
                    }
                }
            }
        }
    })
async def download_file(file_type: str, filename: str):
    """
    Download a specific uploaded file.
    
    Args:
        file_type: Type of file (resume, cv, cover_letter)
        filename: Name of the file to download
        
    Returns:
        FileResponse: File content
        
    Raises:
        HTTPException: If file not found
    """
    try:
        # Validate file type
        if file_type not in ['resume', 'cv', 'cover_letter']:
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Construct file path
        file_path = file_upload_service.upload_dir / file_type / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Return file response
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type=file_upload_service.supported_extensions.get(
                file_path.suffix.lower(), 
                'application/octet-stream'
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File download error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"File download failed: {str(e)}"
        )


@router.delete("/files/{file_type}/{filename}",
    summary="Delete File",
    description="""
    Delete a specific uploaded file.
    
    This endpoint allows deletion of uploaded files for cleanup
    or when files are no longer needed.
    
    ## File Types:
    - **resume**: Resume files
    - **cv**: CV files  
    - **cover_letter**: Cover letter files
    """,
    response_description="File deletion result",
    tags=["Uploads"],
    responses={
        200: {
            "description": "File deleted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "File deleted successfully"
                    }
                }
            }
        },
        404: {
            "description": "File not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "File not found"
                    }
                }
            }
        }
    })
async def delete_file(file_type: str, filename: str):
    """
    Delete a specific uploaded file.
    
    Args:
        file_type: Type of file (resume, cv, cover_letter)
        filename: Name of the file to delete
        
    Returns:
        Dict: Deletion result
        
    Raises:
        HTTPException: If file not found or deletion fails
    """
    try:
        # Validate file type
        if file_type not in ['resume', 'cv', 'cover_letter']:
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Construct file path
        file_path = file_upload_service.upload_dir / file_type / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete file
        file_path.unlink()
        
        logger.info(f"Deleted file: {file_path}")
        
        return {
            "success": True,
            "message": "File deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File deletion error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"File deletion failed: {str(e)}"
        )


@router.post("/cleanup",
    summary="Cleanup Old Files",
    description="""
    Clean up old uploaded files.
    
    This endpoint removes files that are older than the specified
    age to free up storage space.
    
    ## Parameters:
    - **max_age_hours**: Maximum age of files in hours (default: 24)
    """,
    response_description="Cleanup result",
    tags=["Uploads"],
    responses={
        200: {
            "description": "Cleanup completed",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Cleanup completed",
                        "files_removed": 5
                    }
                }
            }
        }
    })
async def cleanup_files(max_age_hours: int = 24):
    """
    Clean up old uploaded files.
    
    Args:
        max_age_hours: Maximum age of files in hours
        
    Returns:
        Dict: Cleanup result
    """
    try:
        files_removed = await file_upload_service.cleanup_old_files(max_age_hours)
        
        return {
            "success": True,
            "message": "Cleanup completed",
            "files_removed": files_removed
        }
        
    except Exception as e:
        logger.error(f"File cleanup error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"File cleanup failed: {str(e)}"
        ) 