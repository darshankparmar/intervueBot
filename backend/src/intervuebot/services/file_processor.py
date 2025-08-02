"""
File processing service for IntervueBot.

This module handles file uploads, parsing, and text extraction from
resume, CV, and cover letter files.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
import aiofiles
import aiohttp
from urllib.parse import urlparse

from intervuebot.schemas.interview import ResumeFile
from intervuebot.core.config import settings

logger = logging.getLogger(__name__)


class FileProcessor:
    """
    File processing service for handling uploaded documents.
    
    This service handles:
    - File download from URLs
    - Text extraction from various file formats
    - File validation and type checking
    - Content parsing and preprocessing
    """
    
    def __init__(self):
        """Initialize the file processor."""
        self.supported_extensions = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.rtf': 'application/rtf'
        }
    
    async def process_uploaded_files(self, files: List[ResumeFile]) -> Dict[str, Any]:
        """
        Process uploaded files and extract text content.
        
        Args:
            files: List of uploaded file information
            
        Returns:
            Dict[str, Any]: Processed file content and metadata
        """
        try:
            logger.info(f"Processing {len(files)} uploaded files")
            
            processed_files = []
            combined_text = ""
            
            for file_info in files:
                # Download and process each file
                file_content = await self._download_file(file_info.file_url)
                if file_content:
                    # Extract text from file
                    extracted_text = await self._extract_text_from_file(
                        file_content, 
                        file_info.filename, 
                        file_info.file_type
                    )
                    
                    if extracted_text:
                        processed_files.append({
                            "filename": file_info.filename,
                            "file_type": file_info.file_type,
                            "content": extracted_text,
                            "size": len(file_content)
                        })
                        combined_text += f"\n\n--- {file_info.filename} ({file_info.file_type}) ---\n{extracted_text}"
            
            return {
                "processed_files": processed_files,
                "combined_text": combined_text.strip(),
                "total_files": len(files),
                "successful_files": len(processed_files),
                "file_types": [f.file_type for f in files]
            }
            
        except Exception as e:
            logger.error(f"Error processing uploaded files: {e}")
            return {
                "processed_files": [],
                "combined_text": "",
                "total_files": len(files),
                "successful_files": 0,
                "error": str(e)
            }
    
    async def _download_file(self, file_url: str) -> Optional[bytes]:
        """
        Download file from URL.
        
        Args:
            file_url: URL of the file to download
            
        Returns:
            Optional[bytes]: File content as bytes
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        logger.warning(f"Failed to download file from {file_url}: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error downloading file from {file_url}: {e}")
            return None
    
    async def _extract_text_from_file(self, file_content: bytes, filename: str, file_type: str) -> Optional[str]:
        """
        Extract text content from file bytes.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            file_type: Type of file (resume, cv, cover_letter)
            
        Returns:
            Optional[str]: Extracted text content
        """
        try:
            # For now, return a placeholder based on file type
            # In production, you would use libraries like:
            # - PyPDF2 or pdfplumber for PDFs
            # - python-docx for DOCX files
            # - python-docx2txt for DOC files
            
            file_extension = Path(filename).suffix.lower()
            
            if file_extension == '.pdf':
                return await self._extract_from_pdf(file_content, file_type)
            elif file_extension in ['.doc', '.docx']:
                return await self._extract_from_word(file_content, file_type)
            elif file_extension == '.txt':
                return await self._extract_from_text(file_content, file_type)
            else:
                logger.warning(f"Unsupported file type: {file_extension}")
                return await self._extract_generic(file_content, file_type)
                
        except Exception as e:
            logger.error(f"Error extracting text from {filename}: {e}")
            return None
    
    async def _extract_from_pdf(self, file_content: bytes, file_type: str) -> str:
        """
        Extract text from PDF file.
        
        Args:
            file_content: PDF file content
            file_type: Type of document
            
        Returns:
            str: Extracted text
        """
        # Placeholder implementation
        # In production, use: pip install PyPDF2 pdfplumber
        return f"""
        {file_type.upper()} DOCUMENT
        
        This is a placeholder for PDF text extraction.
        In production, this would extract actual text from the PDF file.
        
        Sample content for {file_type}:
        - Name: John Doe
        - Experience: 3 years in software development
        - Skills: Python, JavaScript, React, Node.js
        - Education: BS Computer Science
        - Projects: E-commerce platform, API development
        """
    
    async def _extract_from_word(self, file_content: bytes, file_type: str) -> str:
        """
        Extract text from Word document.
        
        Args:
            file_content: Word file content
            file_type: Type of document
            
        Returns:
            str: Extracted text
        """
        # Placeholder implementation
        # In production, use: pip install python-docx
        return f"""
        {file_type.upper()} DOCUMENT
        
        This is a placeholder for Word document text extraction.
        In production, this would extract actual text from the Word file.
        
        Sample content for {file_type}:
        - Professional experience in software development
        - Strong technical skills and problem-solving abilities
        - Experience with modern web technologies
        - Excellent communication and teamwork skills
        """
    
    async def _extract_from_text(self, file_content: bytes, file_type: str) -> str:
        """
        Extract text from plain text file.
        
        Args:
            file_content: Text file content
            file_type: Type of document
            
        Returns:
            str: Extracted text
        """
        try:
            return file_content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return file_content.decode('latin-1')
            except Exception as e:
                logger.error(f"Error decoding text file: {e}")
                return f"Error reading {file_type} file"
    
    async def _extract_generic(self, file_content: bytes, file_type: str) -> str:
        """
        Generic text extraction for unsupported file types.
        
        Args:
            file_content: File content
            file_type: Type of document
            
        Returns:
            str: Generic text content
        """
        try:
            return file_content.decode('utf-8', errors='ignore')
        except Exception as e:
            logger.error(f"Error in generic text extraction: {e}")
            return f"Unable to extract text from {file_type} file"
    
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
            "unsupported_files": 0
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


# Global file processor instance
file_processor = FileProcessor() 