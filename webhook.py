# webhook.py  —  aiogram 3.7 + aiohttp on Render
import asyncio, logging, os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler, setup_application
)
from aiohttp import web
from handlers.survey import router as survey_router

# ─── Config ───────────────────────────────────────────────────────────────────
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN missing")
PORT = int(os.getenv("PORT", 8080))           # Render injects $PORT
BASE_URL = os.getenv("BASE_URL")              # set in Render env-vars
if not BASE_URL:
    raise RuntimeError("Add BASE_URL env var: e.g. https://survey.onrender.com")

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"        # unique secret path
WEBHOOK_URL  = f"{BASE_URL}{WEBHOOK_PATH}"

# ─── Bot & DP ─────────────────────────────────────────────────────────────────
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(survey_router)

# ─── Startup / shutdown hooks ────────────────────────────────────────────────
async def on_startup(bot: Bot):
    await bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)
    logging.info("Webhook set: %s", WEBHOOK_URL)

async def on_shutdown(bot: Bot):
    await bot.delete_webhook()
    logging.info("Webhook deleted")

# ─── aiohttp app ─────────────────────────────────────────────────────────────
def build_app() -> web.Application:
    app = web.Application()
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    ).register(app, path=WEBHOOK_PATH)
    setup_application(
        app,
        bot=bot,
        on_startup=[on_startup],
        on_shutdown=[on_shutdown],
    )
    return app

# ─── Entrypoint ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    web.run_app(build_app(), host="0.0.0.0", port=PORT)
