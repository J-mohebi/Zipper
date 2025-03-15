# zip_utils.py - Utilities for file compression and extraction
import os
import asyncio
import aiofiles
import zipfile
import tarfile
import py7zr
import rarfile
import shutil
from typing import List, Dict, Tuple, Callable, Optional, BinaryIO
import logging
from pathlib import Path

from config import TEMP_DIR, CHUNK_SIZE, COMPRESSION_FORMATS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompressionTask:
    """Class to manage compression tasks with progress tracking"""
    
    def __init__(self, file_path: str, output_format: str, progress_callback: Optional[Callable[[int], None]] = None):
        """
        Initialize a compression task
        
        Args:
            file_path: Path to the file to compress
            output_format: Format to compress to (zip, tar.gz, rar, 7z)
            progress_callback: Callback function to report progress
        """
        self.file_path = file_path
        self.output_format = output_format
        self.progress_callback = progress_callback
        self.canceled = False
        self.total_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        self.processed_size = 0
        
    def update_progress(self, chunk_size: int):
        """Update progress based on processed chunk size"""
        if self.canceled:
            raise asyncio.CancelledError("Task was cancelled")
            
        self.processed_size += chunk_size
        if self.total_size > 0 and self.progress_callback:
            progress = min(int((self.processed_size / self.total_size) * 100), 100)
            asyncio.create_task(self.progress_callback(progress))
            
    def cancel(self):
        """Cancel the task"""
        self.canceled = True

async def compress_file(
    file_path: str, 
    output_format: str = "zip", 
    progress_callback: Optional[Callable[[int], None]] = None
) -> str:
    """
    Compress a file using the specified format with progress tracking
    
    Args:
        file_path: Path to the file to compress
        output_format: Format to compress to (zip, tar.gz, rar, 7z)
        progress_callback: Callback function to report progress
        
    Returns:
        str: Path to the compressed file
    """
    task = CompressionTask(file_path, output_format, progress_callback)
    file_name = os.path.basename(file_path)
    output_path = os.path.join(TEMP_DIR, f"{os.path.splitext(file_name)[0]}{COMPRESSION_FORMATS[output_format]}")
    
    try:
        if output_format == "zip":
            # Use zipfile for ZIP compression
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Get file size for progress tracking
                file_size = os.path.getsize(file_path)
                
                # Open file in binary mode for reading chunks
                async with aiofiles.open(file_path, 'rb') as f:
                    # Process file in chunks to handle large files
                    chunk_size = CHUNK_SIZE
                    bytes_read = 0
                    
                    # Create a temporary file for the chunk
                    temp_chunk_path = os.path.join(TEMP_DIR, f"chunk_{file_name}")
                    
                    while True:
                        chunk = await f.read(chunk_size)
                        if not chunk:
                            break
                            
                        # Write chunk to temporary file
                        async with aiofiles.open(temp_chunk_path, 'wb') as temp_f:
                            await temp_f.write(chunk)
                        
                        # Add the chunk to zip
                        zipf.write(temp_chunk_path, file_name)
                        
                        # Update progress
                        bytes_read += len(chunk)
                        task.update_progress(len(chunk))
                        
                        # Allow other tasks to run
                        await asyncio.sleep(0)
                    
                    # Remove temporary chunk file
                    if os.path.exists(temp_chunk_path):
                        os.remove(temp_chunk_path)
                        
        elif output_format == "tar.gz":
            # Use tarfile for TAR.GZ compression
            with tarfile.open(output_path, "w:gz") as tar:
                # Add file to tar archive
                tar.add(file_path, arcname=os.path.basename(file_path))
                
                # Update progress (approximate as tarfile doesn't provide progress)
                task.update_progress(task.total_size)
                
        elif output_format == "7z":
            # Use py7zr for 7Z compression
            with py7zr.SevenZipFile(output_path, 'w') as archive:
                archive.write(file_path, os.path.basename(file_path))
                
                # Update progress (approximate as py7zr doesn't provide progress)
                task.update_progress(task.total_size)
                
        elif output_format == "rar":
            # Use unrar for RAR compression via subprocess
            # Note: Creating RAR archives requires WinRAR/unrar to be installed
            try:
                process = await asyncio.create_subprocess_exec