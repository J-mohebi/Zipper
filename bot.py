# bot.py - Main execution file for Telegram File Compression Bot
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from pyrogram import Client
from pyrogram.enums import ParseMode as PyrogramParseMode

from config import BOT_TOKEN, API_ID, API_HASH, TEMP_DIR
from handlers import register_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

async def main():
    """Main function to start the bot"""
    logger.info("Starting File Compression Bot...")
    
    # Initialize aiogram bot with default properties
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    
    # Initialize Pyrogram client
    app = Client(
        "file_compression_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        parse_mode=PyrogramParseMode.MARKDOWN
    )
    
    # Initialize dispatcher
    dp = Dispatcher()
    
    # Register all handlers
    register_handlers(dp, bot, app)
    
    # Start Pyrogram client
    await app.start()
    logger.info("Pyrogram client started")
    
    # Start polling
    logger.info("Bot is running...")
    await dp.start_polling(bot)
    
    # Wait until bot is stopped
    await asyncio.Event().wait()
    
    # Cleanup on exit
    await app.stop()
    await bot.session.close()
    logger.info("Bot stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
