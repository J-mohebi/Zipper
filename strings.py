# strings.py - Message strings for the Telegram File Compression Bot
# Supports both English and Persian languages

MESSAGES = {
    "en": {
        "start": "Welcome to File Compression Bot! 📁\n\nI can help you compress and extract files.\n\nSend me any file to begin, or use /help to see available commands.",
        "help": "📚 *Bot Commands:*\n\n"
                "/start - Start the bot\n"
                "/help - Show this help message\n"
                "/cancel - Cancel current operation\n\n"
                "📋 *How to use:*\n\n"
                "1. Send any file to compress it\n"
                "2. Send a compressed file (.zip, .tar.gz, .rar, .7z) to extract it\n"
                "3. Use inline buttons to select desired operations\n\n"
                "⚙️ *Features:*\n"
                "• Multiple compression formats\n"
                "• No file size limits\n"
                "• Fast processing with streaming\n"
                "• Progress tracking\n",
        "file_received": "File received: {}\nSize: {:.2f} MB\n\nWhat would you like to do with this file?",
        "processing": "Processing your file... Please wait.",
        "compressing": "Compressing your file to {}...\n\nProgress: {}%",
        "extracting": "Extracting your file...\n\nProgress: {}%",
        "compression_complete": "Compression complete! Sending the compressed file...",
        "extraction_complete": "Extraction complete! Sending the extracted file(s)...",
        "extraction_too_many_files": "Extraction complete! There are {} files. Sending them as a compressed archive...",
        "task_cancelled": "Task cancelled successfully.",
        "no_active_task": "No active task to cancel.",
        "error_unsupported_format": "Unsupported file format. Supported formats for extraction: zip, tar.gz, rar, 7z",
        "error_processing": "Error processing your file: {}",
        "error_file_corrupted": "The file appears to be corrupted or invalid.",
        "error_extraction": "Could not extract the file. The file might be password-protected or corrupted.",
        "error_compression": "Could not compress the file: {}",
        "compress_format_select": "Select compression format:",
        "file_too_large_telegram": "The file is too large to be sent via Telegram. I'll split it into smaller parts.",
        "split_part": "Part {}/{} of your extraction",
        "preview_content": "Preview of file content:\n\n```\n{}\n```",
        "error_general": "An error occurred: {}. Please try again.",
        "timeout": "Operation timed out. Please try with a smaller file.",
    },
    "fa": {
        "start": "به ربات فشرده‌سازی فایل خوش آمدید! 📁\n\nمن می‌توانم به شما در فشرده‌سازی و استخراج فایل‌ها کمک کنم.\n\nبرای شروع، هر فایلی را برای من ارسال کنید یا از /help برای دیدن دستورات موجود استفاده کنید.",
        "help": "📚 *دستورات ربات:*\n\n"
                "/start - شروع ربات\n"
                "/help - نمایش این پیام راهنما\n"
                "/cancel - لغو عملیات فعلی\n\n"
                "📋 *نحوه استفاده:*\n\n"
                "1. هر فایلی را برای فشرده‌سازی ارسال کنید\n"
                "2. یک فایل فشرده (.zip، .tar.gz، .rar، .7z) برای استخراج ارسال کنید\n"
                "3. از دکمه‌های اینلاین برای انتخاب عملیات مورد نظر استفاده کنید\n\n"
                "⚙️ *ویژگی‌ها:*\n"
                "• فرمت‌های فشرده‌سازی متعدد\n"
                "• بدون محدودیت در اندازه فایل\n"
                "• پردازش سریع با استریمینگ\n"
                "• پیگیری پیشرفت\n",
        "file_received": "فایل دریافت شد: {}\nاندازه: {:.2f} مگابایت\n\nمی‌خواهید با این فایل چه کاری انجام دهید؟",
        "processing": "در حال پردازش فایل شما... لطفاً صبر کنید.",
        "compressing": "در حال فشرده‌سازی فایل شما به {}...\n\nپیشرفت: {}%",
        "extracting": "در حال استخراج فایل شما...\n\nپیشرفت: {}%",
        "compression_complete": "فشرده‌سازی کامل شد! در حال ارسال فایل فشرده...",
        "extraction_complete": "استخراج کامل شد! در حال ارسال فایل(های) استخراج شده...",
        "extraction_too_many_files": "استخراج کامل شد! {} فایل وجود دارد. ارسال آنها به صورت یک آرشیو فشرده...",
        "task_cancelled": "عملیات با موفقیت لغو شد.",
        "no_active_task": "هیچ عملیات فعالی برای لغو وجود ندارد.",
        "error_unsupported_format": "فرمت فایل پشتیبانی نمی‌شود. فرمت‌های پشتیبانی شده برای استخراج: zip، tar.gz، rar، 7z",
        "error_processing": "خطا در پردازش فایل شما: {}",
        "error_file_corrupted": "به نظر می‌رسد فایل خراب یا نامعتبر است.",
        "error_extraction": "استخراج فایل امکان‌پذیر نیست. ممکن است فایل دارای رمز عبور یا خراب باشد.",
        "error_compression": "فشرده‌سازی فایل امکان‌پذیر نیست: {}",
        "compress_format_select": "فرمت فشرده‌سازی را انتخاب کنید:",
        "file_too_large_telegram": "فایل برای ارسال از طریق تلگرام بسیار بزرگ است. آن را به قسمت‌های کوچکتر تقسیم می‌کنم.",
        "split_part": "بخش {}/{} از استخراج شما",
        "preview_content": "پیش‌نمایش محتوای فایل:\n\n```\n{}\n```",
        "error_general": "خطایی رخ داد: {}. لطفاً دوباره تلاش کنید.",
        "timeout": "زمان عملیات به پایان رسید. لطفاً با فایل کوچکتری امتحان کنید.",
    }
}

def get_message(key, lang="en", **kwargs):
    """
    Get a message string in the specified language with optional formatting
    
    Args:
        key (str): The message key
        lang (str): Language code ('en' or 'fa')
        **kwargs: Format parameters for the string
        
    Returns:
        str: The formatted message string
    """
    # Default to English if language not available
    if lang not in MESSAGES:
        lang = "en"
        
    # Get message or default to key name if message not found
    message = MESSAGES[lang].get(key, key)
    
    # Apply formatting if kwargs provided
    if kwargs:
        try:
            return message.format(**kwargs)
        except (KeyError, ValueError):
            return message
    
    return message
