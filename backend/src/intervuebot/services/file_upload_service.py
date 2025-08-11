"""
File upload service for IntervueBot.

This module handles file uploads, storage, and management including
resumes, CVs, and cover letters for interview preparation.
"""

import logging
import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from ..schemas.file import FileInfo
from ..core.config import settings

logger = logging.getLogger(__name__)


class FileUploadService:
    """
    Service for handling file uploads and storage.
    
    This service manages file storage, retrieval, and cleanup
    for interview-related documents.
    """
    
    def __init__(self):
        """Initialize the file upload service."""
        self.upload_dir = Path(settings.UPLOAD_DIR) if hasattr(settings, 'UPLOAD_DIR') else Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.upload_dir / "resumes").mkdir(exist_ok=True)
        (self.upload_dir / "cvs").mkdir(exist_ok=True)
        (self.upload_dir / "cover_letters").mkdir(exist_ok=True)
        
        logger.info(f"File upload service initialized with directory: {self.upload_dir}")
    
    async def store_file(
        self,
        file_id: str,
        filename: str,
        file_type: str,
        content: bytes
    ) -> FileInfo:
        """
        Store a file with unique identifier.
        
        Args:
            file_id: Unique file identifier
            filename: Original filename
            file_type: Type of file (resume, cv, cover_letter)
            content: File content as bytes
            
        Returns:
            FileInfo: File information
        """
        try:
            # Determine subdirectory based on file type
            if file_type == "cv":
                subdir = "cvs"
            elif file_type == "cover_letter":
                subdir = "cover_letters"
            else:
                subdir = "resumes"  # Default to resumes
            
            # Create file path
            file_path = self.upload_dir / subdir / f"{file_id}_{filename}"
            
            # Write file content
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Create file info
            file_info = FileInfo(
                file_id=file_id,
                filename=filename,
                file_type=file_type,
                size=len(content),
                uploaded_at=datetime.utcnow()
            )
            
            logger.info(f"Stored file: {file_id} at {file_path}")
            return file_info
            
        except Exception as e:
            logger.error(f"Failed to store file {file_id}: {e}")
            raise
    
    async def get_file_info(self, file_id: str) -> Optional[FileInfo]:
        """
        Get file information by ID.
        
        Args:
            file_id: Unique file identifier
            
        Returns:
            Optional[FileInfo]: File information or None if not found
        """
        try:
            # Search for file in all subdirectories
            for subdir in ["resumes", "cvs", "cover_letters"]:
                subdir_path = self.upload_dir / subdir
                if subdir_path.exists():
                    for file_path in subdir_path.iterdir():
                        if file_path.name.startswith(file_id + "_"):
                            # Extract filename (remove file_id_ prefix)
                            filename = file_path.name[len(file_id) + 1:]
                            
                            # Determine file type from subdirectory
                            file_type = subdir.rstrip('s')  # Remove 's' from end
                            
                            # Get file size
                            size = file_path.stat().st_size
                            
                            # Get upload time (use file modification time as approximation)
                            uploaded_at = datetime.fromtimestamp(file_path.stat().st_mtime)
                            
                            return FileInfo(
                                file_id=file_id,
                                filename=filename,
                                file_type=file_type,
                                size=size,
                                uploaded_at=uploaded_at
                            )
            
            logger.warning(f"File not found: {file_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get file info for {file_id}: {e}")
            return None
    
    async def get_file_content(self, file_id: str) -> Optional[bytes]:
        """
        Get file content by ID.
        
        Args:
            file_id: Unique file identifier
            
        Returns:
            Optional[bytes]: File content or None if not found
        """
        try:
            # Search for file in all subdirectories
            for subdir in ["resumes", "cvs", "cover_letters"]:
                subdir_path = self.upload_dir / subdir
                if subdir_path.exists():
                    for file_path in subdir_path.iterdir():
                        if file_path.name.startswith(file_id + "_"):
                            with open(file_path, "rb") as f:
                                return f.read()
            
            logger.warning(f"File content not found: {file_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get file content for {file_id}: {e}")
            return None
    
    async def delete_file(self, file_id: str) -> bool:
        """
        Delete a file by ID.
        
        Args:
            file_id: Unique file identifier
            
        Returns:
            bool: True if deleted, False if not found
        """
        try:
            # Search for file in all subdirectories
            for subdir in ["resumes", "cvs", "cover_letters"]:
                subdir_path = self.upload_dir / subdir
                if subdir_path.exists():
                    for file_path in subdir_path.iterdir():
                        if file_path.name.startswith(file_id + "_"):
                            file_path.unlink()
                            logger.info(f"Deleted file: {file_id}")
                            return True
            
            logger.warning(f"File not found for deletion: {file_id}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete file {file_id}: {e}")
            return False
    
    async def list_files(self, file_type: Optional[str] = None) -> List[FileInfo]:
        """
        List all stored files.
        
        Args:
            file_type: Optional filter by file type
            
        Returns:
            List[FileInfo]: List of file information
        """
        try:
            files = []
            
            # Determine which subdirectories to search
            subdirs = [file_type] if file_type else ["resumes", "cvs", "cover_letters"]
            
            for subdir in subdirs:
                subdir_path = self.upload_dir / subdir
                if subdir_path.exists():
                    for file_path in subdir_path.iterdir():
                        if file_path.is_file():
                            # Extract file_id and filename
                            parts = file_path.name.split("_", 1)
                            if len(parts) == 2:
                                file_id, filename = parts
                                
                                # Determine file type from subdirectory
                                actual_file_type = subdir.rstrip('s')
                                
                                # Get file size and upload time
                                size = file_path.stat().st_size
                                uploaded_at = datetime.fromtimestamp(file_path.stat().st_mtime)
                                
                                files.append(FileInfo(
                                    file_id=file_id,
                                    filename=filename,
                                    file_type=actual_file_type,
                                    size=size,
                                    uploaded_at=uploaded_at
                                ))
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []
    
    async def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """
        Clean up old files.
        
        Args:
            max_age_hours: Maximum age in hours before deletion
            
        Returns:
            int: Number of files deleted
        """
        try:
            deleted_count = 0
            cutoff_time = datetime.utcnow().timestamp() - (max_age_hours * 3600)
            
            for subdir in ["resumes", "cvs", "cover_letters"]:
                subdir_path = self.upload_dir / subdir
                if subdir_path.exists():
                    for file_path in subdir_path.iterdir():
                        if file_path.is_file():
                            file_time = file_path.stat().st_mtime
                            if file_time < cutoff_time:
                                file_path.unlink()
                                deleted_count += 1
                                logger.info(f"Cleaned up old file: {file_path.name}")
            
            logger.info(f"Cleanup completed: {deleted_count} files deleted")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old files: {e}")
            return 0


# Global file upload service instance
file_upload_service = FileUploadService() 