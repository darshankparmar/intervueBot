"""
File-related schemas for IntervueBot API.

This module defines the data models for file uploads, storage, and management.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class FileInfo(BaseModel):
    """File information model."""
    
    file_id: str = Field(..., description="Unique file identifier")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="Type of file (resume, cv, cover_letter)")
    size: int = Field(..., description="File size in bytes")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FileUploadResponse(BaseModel):
    """File upload response model."""
    
    status: str = Field(..., description="Upload status (success, partial_success, error)")
    message: str = Field(..., description="Upload result message")
    files: List[FileInfo] = Field(..., description="Successfully uploaded files")
    errors: List[str] = Field(default_factory=list, description="Upload errors if any")


class FileReference(BaseModel):
    """File reference for use in other APIs."""
    
    file_id: str = Field(..., description="Unique file identifier")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="Type of file")


class FileUploadRequest(BaseModel):
    """File upload request model."""
    
    files: List[FileReference] = Field(..., description="Files to process") 