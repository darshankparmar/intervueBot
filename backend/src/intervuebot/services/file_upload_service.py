"""
File upload service for IntervueBot.

This module handles file uploads, storage, validation, and processing
for resumes, CVs, and cover letters.
"""

import os
import uuid
import logging
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
import aiofiles
import aiohttp
from datetime import datetime
from urllib.parse import urlparse

from intervuebot.schemas.interview import ResumeFile
from intervuebot.core.config import settings

logger = logging.getLogger(__name__)


class FileUploadService:
    """
    Service for handling file uploads and storage.
    
    This service handles:
    - File upload validation
    - File storage and organization
    - File type detection and validation
    - File URL generation
    - File metadata management
    """
    
    def __init__(self):
        """Initialize the file upload service."""
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different file types
        self.resume_dir = self.upload_dir / "resumes"
        self.cv_dir = self.upload_dir / "cvs"
        self.cover_letter_dir = self.upload_dir / "cover_letters"
        
        for directory in [self.resume_dir, self.cv_dir, self.cover_letter_dir]:
            directory.mkdir(exist_ok=True)
        
        self.supported_extensions = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.rtf': 'application/rtf'
        }
        
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_file_types = ['resume', 'cv', 'cover_letter']
    
    async def upload_files(self, files: List[Dict[str, Any]]) -> List[ResumeFile]:
        """
        Upload and process multiple files.
        
        Args:
            files: List of file data from frontend
            
        Returns:
            List[ResumeFile]: Processed file information
        """
        try:
            logger.info(f"Processing {len(files)} uploaded files")
            
            uploaded_files = []
            
            for file_data in files:
                try:
                    # Validate file data
                    if not self._validate_file_data(file_data):
                        logger.warning(f"Invalid file data: {file_data.get('name', 'unknown')}")
                        continue
                    
                    # Process and store file
                    resume_file = await self._process_single_file(file_data)
                    if resume_file:
                        uploaded_files.append(resume_file)
                        
                except Exception as e:
                    logger.error(f"Error processing file {file_data.get('name', 'unknown')}: {e}")
                    continue
            
            logger.info(f"Successfully processed {len(uploaded_files)} files")
            return uploaded_files
            
        except Exception as e:
            logger.error(f"Error in upload_files: {e}")
            raise Exception(f"File upload failed: {str(e)}")
    
    def _validate_file_data(self, file_data: Dict[str, Any]) -> bool:
        """
        Validate file data from frontend.
        
        Args:
            file_data: File data from frontend
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ['name', 'type', 'size', 'content']
        
        # Check required fields
        for field in required_fields:
            if field not in file_data:
                logger.warning(f"Missing required field: {field}")
                return False
        
        # Validate file size
        if file_data['size'] > self.max_file_size:
            logger.warning(f"File too large: {file_data['size']} bytes")
            return False
        
        # Validate file type
        if file_data['type'] not in self.allowed_file_types:
            logger.warning(f"Invalid file type: {file_data['type']}")
            return False
        
        # Validate file extension
        file_extension = Path(file_data['name']).suffix.lower()
        if file_extension not in self.supported_extensions:
            logger.warning(f"Unsupported file extension: {file_extension}")
            return False
        
        return True
    
    async def _process_single_file(self, file_data: Dict[str, Any]) -> Optional[ResumeFile]:
        """
        Process a single file upload.
        
        Args:
            file_data: File data from frontend
            
        Returns:
            Optional[ResumeFile]: Processed file information
        """
        try:
            # Generate unique filename
            original_name = file_data['name']
            file_extension = Path(original_name).suffix.lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Determine storage directory based on file type
            if file_data['type'] == 'resume':
                storage_dir = self.resume_dir
            elif file_data['type'] == 'cv':
                storage_dir = self.cv_dir
            elif file_data['type'] == 'cover_letter':
                storage_dir = self.cover_letter_dir
            else:
                storage_dir = self.upload_dir
            
            # Create file path
            file_path = storage_dir / unique_filename
            
            # Decode and save file content
            file_content = file_data['content']
            if isinstance(file_content, str):
                # Handle base64 encoded content
                import base64
                file_bytes = base64.b64decode(file_content.split(',')[1] if ',' in file_content else file_content)
            else:
                file_bytes = file_content
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_bytes)
            
            # Generate file URL
            file_url = f"/uploads/{file_data['type']}/{unique_filename}"
            
            # Create ResumeFile object
            resume_file = ResumeFile(
                filename=original_name,
                file_url=file_url,
                file_type=file_data['type']
            )
            
            logger.info(f"Successfully processed file: {original_name} -> {file_path}")
            return resume_file
            
        except Exception as e:
            logger.error(f"Error processing file {file_data.get('name', 'unknown')}: {e}")
            return None
    
    async def get_file_content(self, file_url: str) -> Optional[bytes]:
        """
        Get file content from URL.
        
        Args:
            file_url: File URL
            
        Returns:
            Optional[bytes]: File content
        """
        try:
            # Parse URL and get file path
            parsed_url = urlparse(file_url)
            file_path = self.upload_dir / parsed_url.path.lstrip('/uploads/')
            
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                return None
            
            # Read file content
            async with aiofiles.open(file_path, 'rb') as f:
                content = await f.read()
            
            return content
            
        except Exception as e:
            logger.error(f"Error reading file {file_url}: {e}")
            return None
    
    def validate_file_type(self, filename: str) -> bool:
        """
        Validate if file type is supported.
        
        Args:
            filename: Name of the file
            
        Returns:
            bool: True if file type is supported
        """
        file_extension = Path(filename).suffix.lower()
        return file_extension in self.supported_extensions
    
    def get_file_metadata(self, files: List[ResumeFile]) -> Dict[str, Any]:
        """
        Get metadata about uploaded files.
        
        Args:
            files: List of uploaded files
            
        Returns:
            Dict[str, Any]: File metadata
        """
        metadata = {
            "total_files": len(files),
            "file_types": {},
            "supported_files": 0,
            "unsupported_files": 0,
            "total_size": 0
        }
        
        for file_info in files:
            file_type = file_info.file_type
            if file_type not in metadata["file_types"]:
                metadata["file_types"][file_type] = 0
            metadata["file_types"][file_type] += 1
            
            if self.validate_file_type(file_info.filename):
                metadata["supported_files"] += 1
            else:
                metadata["unsupported_files"] += 1
        
        return metadata
    
    async def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """
        Clean up old uploaded files.
        
        Args:
            max_age_hours: Maximum age of files in hours
            
        Returns:
            int: Number of files cleaned up
        """
        try:
            cleaned_count = 0
            cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
            
            for directory in [self.resume_dir, self.cv_dir, self.cover_letter_dir]:
                for file_path in directory.iterdir():
                    if file_path.is_file():
                        file_age = file_path.stat().st_mtime
                        if file_age < cutoff_time:
                            file_path.unlink()
                            cleaned_count += 1
                            logger.info(f"Cleaned up old file: {file_path}")
            
            logger.info(f"Cleaned up {cleaned_count} old files")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old files: {e}")
            return 0


# Global file upload service instance
file_upload_service = FileUploadService() 