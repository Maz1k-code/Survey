from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardRemove
)
from utils.storage import store_row

router = Router()

# ─── Inline-button helpers ────────────────────────────────────────────────────
def kb_confirm_repeat():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_basic"),
            InlineKeyboardButton(text="🔄 Повторить опрос", callback_data="repeat_basic")
        ]
    ])

def kb_confirm_video():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_video"),
            InlineKeyboardButton(text="🔄 Записать заново", callback_data="repeat_video")
        ]
    ])

# ─── FSM states ───────────────────────────────────────────────────────────────
class Survey(StatesGroup):
    name        = State()   # Q1
    city        = State()   # Q2
    one_liner   = State()   # Q3
    metrics     = State()   # Q4
    funding     = State()   # Q5
    confirm     = State()   # waiting Confirm / Repeat
    video       = State()   # Q6
    confirm_vid = State()   # waiting Confirm / Repeat
    media       = State()   # Q7

# ─── /start entry ─────────────────────────────────────────────────────────────
@router.message(Command("start", "help"))
async def cmd_start(msg: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Survey.name)
    await msg.answer("👋 Привет! 1️⃣ Название проекта?")

# ─── Q1 → Q2 ──────────────────────────────────────────────────────────────────
@router.message(Survey.name, F.text)
async def q1_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text.strip())
    await state.set_state(Survey.city)
    await msg.answer("2️⃣ Город?")

# ─── Q2 → Q3 ──────────────────────────────────────────────────────────────────
@router.message(Survey.city, F.text)
async def q2_city(msg: Message, state: FSMContext):
    await state.update_data(city=msg.text.strip())
    await state.set_state(Survey.one_liner)
    await msg.answer("3️⃣ Опиши проект одной фразой")

# ─── Q3 → Q4 ──────────────────────────────────────────────────────────────────
@router.message(Survey.one_liner, F.text)
async def q3_one_liner(msg: Message, state: FSMContext):
    await state.update_data(one_liner=msg.text.strip())
    await state.set_state(Survey.metrics)
    await msg.answer("4️⃣ Опиши главные метрики (Выручка, Пользователи, Прибыль и т.п.)")

# ─── Q4 → Q5 ──────────────────────────────────────────────────────────────────
@router.message(Survey.metrics, F.text)
async def q4_metrics(msg: Message, state: FSMContext):
    await state.update_data(metrics=msg.text.strip())
    await state.set_state(Survey.funding)
    await msg.answer("5️⃣ Сколько денег ищете и на что?")

# ─── Q5 → show summary & ask for confirm ──────────────────────────────────────
@router.message(Survey.funding, F.text)
async def q5_funding(msg: Message, state: FSMContext):
    await state.update_data(funding=msg.text.strip())
    data = await state.get_data()

    summary = (
        "<b>Проверьте данные</b>:\n"
        f"• Название: {data['name']}\n"
        f"• Город: {data['city']}\n"
        f"• ⟪One-liner⟫: {data['one_liner']}\n"
        f"• Метрики: {data['metrics']}\n"
        f"• Запрос: {data['funding']}"
    )
    await state.set_state(Survey.confirm)
    await msg.answer(summary, reply_markup=kb_confirm_repeat())

# ─── Handle Confirm / Repeat for basic part ───────────────────────────────────
@router.callback_query(StateFilter(Survey.confirm), F.data == "confirm_basic")
async def cb_confirm_basic(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(Survey.video)
    await cb.message.answer(
        "6️⃣ Запиши кружок (video note) с питчем проекта"
    )

@router.callback_query(StateFilter(Survey.confirm), F.data == "repeat_basic")
async def cb_repeat_basic(cb: CallbackQuery, state: FSMContext):
    await cb.answer("Начинаем заново")
    await state.clear()
    await state.set_state(Survey.name)
    await cb.message.answer("1️⃣ Название проекта?")

# ─── Accept video note ────────────────────────────────────────────────────────
@router.message(Survey.video, F.content_type.video_note)
async def q6_video(msg: Message, state: FSMContext):
    await state.update_data(video_file_id=msg.video_note.file_id)
    await state.set_state(Survey.confirm_vid)
    await msg.answer("Сохранить это видео?", reply_markup=kb_confirm_video())

# If user sends something other than video_note
@router.message(Survey.video)
async def video_wrong(msg: Message):
    await msg.answer("Пожалуйста, пришлите именно <b>кружок</b> (video note).")

# ─── Confirm / Repeat video ───────────────────────────────────────────────────
@router.callback_query(StateFilter(Survey.confirm_vid), F.data == "confirm_video")
async def cb_confirm_video(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(Survey.media)
    await cb.message.answer(
        "7️⃣ Пришлите фотографии продукта и/или PDF-презентацию.\n"
        "Можно несколько файлов. Когда закончите — отправьте /done",
        reply_markup=ReplyKeyboardRemove()
    )

@router.callback_query(StateFilter(Survey.confirm_vid), F.data == "repeat_video")
async def cb_repeat_video(cb: CallbackQuery, state: FSMContext):
    await state.update_data(video_file_id=None)
    await state.set_state(Survey.video)
    await cb.answer()
    await cb.message.answer("Окей, запишите кружок снова.")

# ─── Collect media (photos + PDFs) ────────────────────────────────────────────
@router.message(Survey.media, F.content_type.photo | F.content_type.document)
async def q7_media(msg: Message, state: FSMContext):
    data = await state.get_data()
    media_list = data.get("media", [])
    if msg.photo:
        media_list.append(msg.photo[-1].file_id)          # highest resolution
    elif msg.document and msg.document.mime_type == "application/pdf":
        media_list.append(msg.document.file_id)
    else:
        await msg.answer("⛔️ Только фото или PDF-файл.")
        return

    await state.update_data(media=media_list)
    await msg.answer("✅ Сохранено. Можно прислать ещё или /done если всё.")

# /done finishes the whole survey
@router.message(Survey.media, Command("done"))
async def finish(msg: Message, state: FSMContext):
    data = await state.get_data()
    store_row(data)   # append full record (utils/storage.py)

    await msg.answer("🎉 Спасибо! Заявка отправлена.")
    await state.clear()
