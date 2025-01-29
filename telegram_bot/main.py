import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv
from db import add_user, get_user

# Încărcăm variabilele de mediu
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Definim stările pentru colectarea datelor utilizatorului
class UserForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_email = State()

# /start - Afișează un buton pentru selecția tipului de utilizator
@dp.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏢 Company", callback_data="user_type:Company")],
        [InlineKeyboardButton(text="👤 Individual", callback_data="user_type:Individual")]
    ])

    await message.answer("👋 Salut! Selectează tipul tău de utilizator:", reply_markup=keyboard)

# Selectează tipul de utilizator
@dp.callback_query(F.data.startswith("user_type:"))
async def user_type_selected(callback: CallbackQuery, state: FSMContext):
    user_type = callback.data.split(":")[1]
    
    # Salvăm tipul de utilizator în FSM (Finite State Machine)
    await state.update_data(user_type=user_type)
    
    await callback.message.answer("✍️ Introdu numele tău:")
    await state.set_state(UserForm.waiting_for_name)

# Salvăm numele și solicităm telefonul
@dp.message(UserForm.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    
    await message.answer("📞 Introdu numărul tău de telefon:")
    await state.set_state(UserForm.waiting_for_phone)

# Salvăm telefonul și solicităm emailul
@dp.message(UserForm.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    
    await message.answer("📧 Introdu adresa ta de email:")
    await state.set_state(UserForm.waiting_for_email)

# Salvăm emailul și înregistrăm utilizatorul în baza de date
@dp.message(UserForm.waiting_for_email)
async def process_email(message: Message, state: FSMContext):
    user_data = await state.get_data()

    # Salvăm utilizatorul în baza de date
    await add_user(
        telegram_id=message.from_user.id,
        name=user_data["name"],
        phone=user_data["phone"],
        email=message.text,
        user_type=user_data["user_type"]
    )

    await message.answer("✅ Datele tale au fost salvate cu succes!")
    await state.clear()  # Resetăm starea FSM

# Pornirea botului
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
