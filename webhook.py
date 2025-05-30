# webhook.py  —  aiogram 3.7 + aiohttp on Render (webhook mode)

import asyncio, logging, os
from dotenv import load_dotenv
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application
)
from handlers.survey import router as survey_router

# ─── Config ───────────────────────────────────────────────────────────────────
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN missing")

PORT = int(os.getenv("PORT", 8080))            # Render injects $PORT
BASE_URL = os.getenv("BASE_URL")               # env-var you added in Render
if not BASE_URL:
    raise RuntimeError("Set BASE_URL (e.g. https://survey-bot.onrender.com)")

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"         # unique secret path
WEBHOOK_URL  = f"{BASE_URL}{WEBHOOK_PATH}"

# ─── Bot & Dispatcher ─────────────────────────────────────────────────────────
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(survey_router)

# ─── Startup / shutdown hooks ────────────────────────────────────────────────
async def on_startup(_: Dispatcher):
    await bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)
    logging.info("Webhook set: %s", WEBHOOK_URL)

async def on_shutdown(_: Dispatcher):
    await bot.delete_webhook()
    logging.info("Webhook deleted")

# ─── aiohttp application factory ─────────────────────────────────────────────
def build_app() -> web.Application:
    app = web.Application()
    # handler that routes Telegram POSTs to the dispatcher
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    ).register(app, path=WEBHOOK_PATH)

    # tell aiogram to plug its startup/shutdown into aiohttp’s lifecycle
    setup_application(
        app,
        dp,                     # ← dispatcher is REQUIRED positional arg
        bot=bot,
        on_startup=[on_startup],
        on_shutdown=[on_shutdown],
    )
    return app

# ─── Entrypoint ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    web.run_app(build_app(), host="0.0.0.0", port=PORT)
