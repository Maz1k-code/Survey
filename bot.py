import asyncio
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

# Import the router object explicitly
from handlers.survey import router as survey_router

# ─── Configuration ────────────────────────────────────────────────────────────
load_dotenv()                                     # reads .env in the project root
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Add it to your .env file.")

# ─── Main coroutine ───────────────────────────────────────────────────────────
async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )

    # Bot instance with default HTML parse mode (new syntax for aiogram 3.7+)
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Dispatcher with in-memory FSM storage
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(survey_router)              # register survey conversation

    # Start polling (press Ctrl-C to stop)
    await dp.start_polling(bot)

# ─── Entrypoint ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    asyncio.run(main())
