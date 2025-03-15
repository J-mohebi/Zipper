# handlers.py - Command and message handlers for Telegram File Compression Bot
import os
import asyncio
import logging
import time
from typing import Dict, Any, Optional, Union, List, Tuple
import mimetypes
from datetime import datetime
import aiofiles
from aiogram import Router, F, Dispatcher, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pyrogram import Client
from pyrogram.types import Message as PyrogramMessage

from config import TEMP_DIR, COMPRESSION_FORMATS, MAX_PREVIEW_SIZE, FILE_STORAGE_TIME, MAX_CONCURRENT_TASKS
from strings import get_message
from zip_utils import compress_file, extract_archive, is_archive_file, get_file_info, clean_temp_files

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store user active tasks and languages
user_tasks: Dict[int, Dict[str, Any]] = {}
user_languages: Dict[int, str] = {}
concurrent_tasks = 0

# Setup routers
main_router = Router()
callback_router = Router()

# Clean old files periodically
async def clean_old_files():
    """Clean old temporary files periodically"""
    while True:
        try:
            await clean_temp_files(hours=FILE_STORAGE_TIME)
            await asyncio.sleep(3600)  # Check every hour
        except Exception as e:
            logger.error(f"Error cleaning old files: {e}")
            await asyncio.sleep(3600)

# Register command handlers
@main_router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle the /start command"""
    user_id = message.from_user.id
    lang = get_user_language(message)
    
    # Save user language preference
    user_languages[user_id] = lang
    
    await message.answer(get_message("start", lang))

@main_router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle the /help command"""
    lang = get_user_language(message)
    await message.answer(get_message("help", lang))

@main_router.message(Command("cancel"))
async def cmd_cancel(message: Message):
    """Handle the /cancel command - cancels active task"""
    user_id = message.from_user.id
    lang = get_user_language(message)
    
    if user_id in user_tasks and user_tasks[user_id].get("task"):
        # Cancel the task
        task = user_tasks[user_id]["task"]
        if not task.done():
            task.cancel()
        
        # Clean up resources
        if "temp_files" in user_tasks[user_id]:
            for temp_file in user_tasks[user_id]["temp_files"]:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except Exception as e:
                        logger.error(f"Error removing temp file: {e}")
        
        # Clear user task
        user_tasks[user_id] = {}
        
        await message.answer(get_message("task_cancelled", lang))
    else:
        await message.answer(get_message("no_active_task", lang))

# Handle file messages
@main_router.message(F.document)
async def handle_document(message: Message, bot: Bot):
    """Handle document messages (files)"""
    global concurrent_tasks
    
    user_id = message.from_user.id
    lang = get_user_language(message)
    
    # Check if user has an active task
    if user_id in user_tasks and user_tasks[user_id].get("task") and not user_tasks[user_id].get("task").done():
        await message.answer(get_message("processing", lang))
        return
    
    # Check concurrent task limit
    if concurrent_tasks >= MAX_CONCURRENT_TASKS:
        await message.answer(get_message("error_general", lang, error="Too many active tasks. Please try again later."))
        return
    
    # Initialize user task
    user_tasks[user_id] = {"temp_files": []}
    
    try:
        # Get file info
        file_id = message.document.file_id
        file_name = message.document.file_name or "unknown_file"
        file_size = message.document.file_size or 0
        file_size_mb = file_size / (1024 * 1024)
        
        # Create temp directory for user if it doesn't exist
        user_temp_dir = os.path.join(TEMP_DIR, str(user_id))
        os.makedirs(user_temp_dir, exist_ok=True)
        
        # Get file path to download
        file_path = os.path.join(user_temp_dir, file_name)
        user_tasks[user_id]["temp_files"].append(file_path)
        
        # Inform user
        await message.answer(get_message("file_received", lang, file_name=file_name, file_size_mb=file_size_mb))
        
        # Download file
        await message.answer(get_message("processing", lang))
        await bot.download(file=file_id, destination=file_path)
        
        # Check if file is an archive
        if is_archive_file(file_path):
            # Show extract button
            builder = InlineKeyboardBuilder()
            builder.button(text="📂 Extract", callback_data=f"extract:{file_path}")
            builder.button(text="🔎 Preview", callback_data=f"preview:{file_path}")
            await message.answer("Choose action:", reply_markup=builder.as_markup())
        else:
            # Show compression format options
            builder = InlineKeyboardBuilder()
            for format_name in COMPRESSION_FORMATS:
                builder.button(text=f"📦 {format_name.upper()}", callback_data=f"compress:{file_path}:{format_name}")
            builder.adjust(2)
            await message.answer(get_message("compress_format_select", lang), reply_markup=builder.as_markup())
    
    except Exception as e:
        logger.error(f"Error handling document: {e}", exc_info=True)
        await message.answer(get_message("error_processing", lang, error=str(e)))
        
        # Clean up
        if user_id in user_tasks:
            for temp_file in user_tasks[user_id].get("temp_files", []):
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except Exception as e:
                        logger.error(f"Error removing temp file: {e}")
            user_tasks[user_id] = {}

# Handle callback queries
@callback_router.callback_query(F.data.startswith("compress:"))
async def compress_callback(callback: CallbackQuery, bot: Bot):
    """Handle compression callback queries"""
    global concurrent_tasks
    
    await callback.answer()
    user_id = callback.from_user.id
    lang = user_languages.get(user_id, "en")
    
    # Parse callback data
    _, file_path, format_name = callback.data.split(":", 2)
    
    if not os.path.exists(file_path):
        await callback.message.answer(get_message("error_processing", lang, error="File not found"))
        return
    
    # Update user task
    user_tasks[user_id]["operation"] = "compress"
    user_tasks[user_id]["file_path"] = file_path
    user_tasks[user_id]["format"] = format_name
    
    try:
        # Increment concurrent tasks
        concurrent_tasks += 1
        
        # Update progress message
        progress_message = await callback.message.answer(
            get_message("compressing", lang, format=format_name.upper(), progress=0)
        )
        
        # Define progress callback
        async def update_progress(progress: int):
            try:
                await bot.edit_message_text(
                    get_message("compressing", lang, format=format_name.upper(), progress=progress),
                    chat_id=callback.message.chat.id,
                    message_id=progress_message.message_id
                )
            except Exception as e:
                logger.error(f"Error updating progress: {e}")
        
        # Start compression task
        task = asyncio.create_task(compress_file(file_path, format_name, update_progress))
        user_tasks[user_id]["task"] = task
        
        # Wait for compression to complete
        output_path = await task
        user_tasks[user_id]["temp_files"].append(output_path)
        
        # Send compressed file
        await callback.message.answer(get_message("compression_complete", lang))
        
        # Check file size
        if os.path.getsize(output_path) > 50 * 1024 * 1024:  # 50MB (Telegram limit)
            await callback.message.answer(get_message("file_too_large_telegram", lang))
            
            # Split file into parts and send
            await split_and_send_file(output_path, callback.message.chat.id, bot, lang)
        else:
            # Send compressed file
            await bot.send_document(
                callback.message.chat.id,
                document=output_path,
                caption=f"Compressed file ({format_name.upper()})"
            )
        
        # Clean up
        for temp_file in user_tasks[user_id].get("temp_files", []):
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    logger.error(f"Error removing temp file: {e}")
        
        user_tasks[user_id] = {}
        
    except asyncio.CancelledError:
        await callback.message.answer(get_message("task_cancelled", lang))
    except Exception as e:
        logger.error(f"Error compressing file: {e}", exc_info=True)
        await callback.message.answer(get_message("error_compression", lang, error=str(e)))
    finally:
        # Decrement concurrent tasks
        concurrent_tasks -= 1

@callback_router.callback_query(F.data.startswith("extract:"))
async def extract_callback(callback: CallbackQuery, bot: Bot):
    """Handle extraction callback queries"""
    global concurrent_tasks
    
    await callback.answer()
    user_id = callback.from_user.id
    lang = user_languages.get(user_id, "en")
    
    # Parse callback data
    _, file_path = callback.data.split(":", 1)
    
    if not os.path.exists(file_path):
        await callback.message.answer(get_message("error_processing", lang, error="File not found"))
        return
    
    # Update user task
    user_tasks[user_id]["operation"] = "extract"
    user_tasks[user_id]["file_path"] = file_path
    
    try:
        # Increment concurrent tasks
        concurrent_tasks += 1
        
        # Create extraction directory
        extract_dir = os.path.join(TEMP_DIR, f"{user_id}_extracted_{int(time.time())}")
        os.makedirs(extract_dir, exist_ok=True)
        user_tasks[user_id]["extract_dir"] = extract_dir
        
        # Update progress message
        progress_message = await callback.message.answer(
            get_message("extracting", lang, progress=0)
        )
        
        # Define progress callback
        async def update_progress(progress: int):
            try:
                await bot.edit_message_text(
                    get_message("extracting", lang, progress=progress),
                    chat_id=callback.message.chat.id,
                    message_id=progress_message.message_id
                )
            except Exception as e:
                logger.error(f"Error updating progress: {e}")
        
        # Start extraction task
        task = asyncio.create_task(extract_archive(file_path, extract_dir, update_progress))
        user_tasks[user_id]["task"] = task
        
        # Wait for extraction to complete
        extracted_files = await task
        
        # Send extracted files
        await callback.message.answer(get_message("extraction_complete", lang))
        
        # If there are too many files, compress them and send as a single archive
        if len(extracted_files) > 10:
            await callback.message.answer(
                get_message("extraction_too_many_files", lang, count=len(extracted_files))
            )
            
            # Create a zip of extracted files
            zip_path = os.path.join(TEMP_DIR, f"extracted_files_{user_id}.zip")
            user_tasks[user_id]["temp_files"].append(zip_path)
            
            # Define progress callback for compression
            async def update_zip_progress(progress: int):
                try:
                    await bot.edit_message_text(
                        get_message("compressing", lang, format="ZIP", progress=progress),
                        chat_id=callback