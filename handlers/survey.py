from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from utils.storage import store_row

router = Router()

# ─── FSM states ─────────────────────────────────────────────
class Survey(StatesGroup):
    company   = State()
    website   = State()
    contact   = State()
    one_liner = State()
    funding   = State()

# ─── /start entry ───────────────────────────────────────────
@router.message(Command("start", "help"))
async def cmd_start(msg: Message, state: FSMContext):
    await state.set_state(Survey.company)
    await msg.answer("👋 Привет! 1️⃣ Название компании?")

# ─── Q1 → Q2 ────────────────────────────────────────────────
@router.message(Survey.company, F.text)
async def q1_company(msg: Message, state: FSMContext):
    await state.update_data(company=msg.text.strip())
    await state.set_state(Survey.website)
    await msg.answer("2️⃣ Сайт или ссылка на презентацию:")

# ─── Q2 → Q3 ────────────────────────────────────────────────
@router.message(Survey.website, F.text)
async def q2_website(msg: Message, state: FSMContext):
    await state.update_data(website=msg.text.strip())
    await state.set_state(Survey.contact)
    await msg.answer("3️⃣ Контактное лицо (имя + email/Telegram):")

# ─── Q3 → Q4 ────────────────────────────────────────────────
@router.message(Survey.contact, F.text)
async def q3_contact(msg: Message, state: FSMContext):
    await state.update_data(contact=msg.text.strip())
    await state.set_state(Survey.one_liner)
    await msg.answer("4️⃣ Одним предложением: чем вы занимаетесь?")

# ─── Q4 → Q5 ────────────────────────────────────────────────
@router.message(Survey.one_liner, F.text)
async def q4_one_liner(msg: Message, state: FSMContext):
    await state.update_data(one_liner=msg.text.strip())
    await state.set_state(Survey.funding)
    await msg.answer("5️⃣ Сколько средств планируете привлечь?")

# ─── Finish ────────────────────────────────────────────────
@router.message(Survey.funding, F.text)
async def q5_funding(msg: Message, state: FSMContext):
    await state.update_data(funding=msg.text.strip())

    data = await state.get_data()
    store_row(data)                                   # write to CSV

    await msg.answer(
        "✅ Спасибо! Мы свяжемся при отборе.",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()
