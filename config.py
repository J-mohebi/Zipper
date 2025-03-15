# config.py - Configuration file for the Telegram File Compression Bot
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot API Token (from BotFather)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Pyrogram API credentials
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

# Maximum number of concurrent tasks
MAX_CONCURRENT_TASKS = 5

# Temporary directory for file processing
TEMP_DIR = "temp_files"

# Create temp directory if it doesn't exist
os.makedirs(TEMP_DIR, exist_ok=True)

# Maximum chunk size for file processing (in bytes) - 10MB
CHUNK_SIZE = 10 * 1024 * 1024

# Supported compression formats
COMPRESSION_FORMATS = {
    "zip": ".zip",
    "tar.gz": ".tar.gz",
    "rar": ".rar",
    "7z": ".7z"
}

# Maximum file size for preview text (in bytes) - 1MB
MAX_PREVIEW_SIZE = 1 * 1024 * 1024

# User file storage time limit (in hours)
FILE_STORAGE_TIME = 24
