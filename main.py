import asyncio,os
from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery
from datetime import datetime
load_dotenv()

TOKEN = getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()


# =========================
#  STATE
# =========================
class Form(StatesGroup):
    waiting_for_birthdate = State()


# =========================
#  /START
# =========================
@dp.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.set_state(Form.waiting_for_birthdate)
    await message.answer("Salom Tug'ilgan sanangizni kiriting (dd/mm/yyyy):")


# =========================
#  BIRTHDATE QABUL QILISH
# =========================
@dp.message(Form.waiting_for_birthdate)
async def get_birthdate(message: Message, state: FSMContext):
    try:
        birth_date = datetime.strptime(message.text, "%d/%m/%Y")

        # sanani state ichida saqlaymiz
        await state.update_data(birth_date=birth_date.isoformat())

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="⌛Sekund", callback_data="seconds"),
                    InlineKeyboardButton(text="🗓️Oy", callback_data="months"),
                ],
                [
                    InlineKeyboardButton(text="📅Kun", callback_data="days"),
                    InlineKeyboardButton(text="🗓️Hafta", callback_data="weeks"),
                ]
            ]
        )

        await message.answer("Qaysi birlikda hisoblaymiz?", reply_markup=keyboard)

    except ValueError:
        await message.answer("❌ Noto'g'ri format! Iltimos dd/mm/yyyy formatda kiriting.")


# =========================
#  INLINE TUGMALAR
# =========================
@dp.callback_query()
async def calculate_life(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if "birth_date" not in data:
        await callback.message.answer("Avval /start bosing.")
        return

    birth_date = datetime.fromisoformat(data["birth_date"])
    now = datetime.now()
    diff = now - birth_date

    action = callback.data

    if action == "seconds":
        result = int(diff.total_seconds())
        text = f"⏳ Siz {result:,} sekund yashagansiz."
    elif action == "days":
        result = diff.days
        text = f"📅 Siz {result:,} kun yashagansiz."
    elif action == "weeks":
        result = diff.days // 7
        text = f"🗓 Siz {result:,} hafta yashagansiz."
    elif action == "months":
        result = diff.days // 30
        text = f"📆 Siz taxminan {result:,} oy yashagansiz."
    else:
        text = "Noma'lum amal."

    await callback.message.answer(text)
    await callback.answer()


# =========================
#  MAIN
# =========================
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

