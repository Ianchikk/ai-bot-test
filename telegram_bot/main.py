import asyncio
import logging
import os
import platform
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv
from db import add_user, get_user
from ai import ask_openai 

# Setăm SelectorEventLoop pe Windows pentru compatibilitate cu aiodns
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

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
async def start_command(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Ask an additional question", callback_data="ask_ai")],
        [InlineKeyboardButton(text="🏢 Company", callback_data="user_type:Company")],
        [InlineKeyboardButton(text="👤 Individual", callback_data="user_type:Individual")]
    ])
    await message.answer("👋 Salut! Selectează o opțiune:", reply_markup=keyboard)

@dp.callback_query(F.data == "ask_ai")
async def ask_ai_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🤖 Introdu întrebarea ta pentru AI:")
    await state.set_state("waiting_for_ai_question")

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

@dp.message(Command("ask"))
async def ask_ai(message: Message, state: FSMContext):
    await message.answer("🤖 Introdu întrebarea ta pentru AI:")
    await state.set_state("waiting_for_ai_question")

@dp.message(F.state == "waiting_for_ai_question")
async def process_ai_question(message: Message, state: FSMContext):
    user_question = message.text
    await message.answer("⏳ Gândesc...")

    try:
        print(f"📨 Întrebare primită: {user_question}")  # Debugging

        response = await ask_openai(user_question)

        print(f"✅ Răspuns OpenAI: {response}")  # Debugging
        await message.answer(f"💬 **Răspuns AI:**\n{response}")

    except Exception as e:
        print(f"❌ Eroare în handler-ul AI: {e}")
        await message.answer(f"❌ Eroare la procesarea cererii: {e}")

    await state.clear()

# Pornirea botului
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
