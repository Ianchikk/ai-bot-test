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
from ai import ask_openai  # Importăm funcția pentru OpenAI
from db import add_user, get_user  # Importăm funcțiile pentru baza de date
from bitrix import create_deal, add_comment_to_deal, notify_manager

# Setăm event loop corect pentru Windows
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Încărcăm variabilele de mediu
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Inițializăm botul și dispatcher-ul
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Definim stările FSM pentru colectarea datelor utilizatorului
class UserForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_email = State()

# /start - Afișează meniul cu opțiuni
@dp.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏢 Company", callback_data="user_type:Company")],
        [InlineKeyboardButton(text="👤 Individual", callback_data="user_type:Individual")]
    ])
    await message.answer("👋 Salut! Selectează o opțiune:", reply_markup=keyboard)

# Handler pentru selecția tipului de utilizator (Company / Individual)
@dp.callback_query(F.data.startswith("user_type:"))
async def user_type_selected(callback: CallbackQuery, state: FSMContext):
    user_type = callback.data.split(":")[1]
    
    await state.update_data(user_type=user_type)
    
    await callback.message.answer(f"✅ Ai selectat: {user_type}\n✍️ Introdu numele tău:")
    await state.set_state(UserForm.waiting_for_name)
    await callback.answer()

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

# Salvăm datele utilizatorului în PostgreSQL și afișăm butonul AI
@dp.message(UserForm.waiting_for_email)
async def process_email(message: Message, state: FSMContext):
    user_data = await state.get_data()

    # Creăm un deal în Bitrix24
    deal_id = create_deal(
        name=user_data["name"],
        phone=user_data["phone"],
        email=message.text,
        user_type=user_data["user_type"]
    )

    if deal_id:
        # Salvăm utilizatorul în PostgreSQL cu deal_id
        await add_user(
            telegram_id=message.from_user.id,
            name=user_data["name"],
            phone=user_data["phone"],
            email=message.text,
            user_type=user_data["user_type"],
            deal_id=deal_id
        )

        await message.answer(f"✅ Informațiile tale au fost salvate și s-a creat un deal în Bitrix24 cu ID-ul: {deal_id}")

        # Afișăm butoanele interactive
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💬 Ask an additional question", callback_data=f"ask_ai_{deal_id}")],
            [InlineKeyboardButton(text="📞 Contact the manager", callback_data=f"contact_manager_{deal_id}")],
            [InlineKeyboardButton(text="💳 Proceed to payment", url="https://your-payment-link.com")]
        ])
        await message.answer("Alege o opțiune:", reply_markup=keyboard)

    else:
        await message.answer("❌ Eroare la crearea deal-ului în Bitrix24. Încearcă din nou.")

    await state.clear()



# Handler pentru butonul "Ask an AI question"
@dp.callback_query(F.data.startswith("ask_ai_"))
async def ask_ai_callback(callback: CallbackQuery):
    deal_id = callback.data.split("_")[2]
    await callback.message.answer(f"🤖 Introdu întrebarea ta pentru AI (va fi salvată în Deal ID {deal_id}):")
    await callback.answer()

@dp.message()
async def process_ai_question(message: Message):
    user = await get_user(message.from_user.id)

    if not user:
        await message.answer("⚠️ Trebuie să te înregistrezi înainte de a pune întrebări AI.\n"
                             "Folosește /start pentru a începe!")
        return

    deal_id = user["deal_id"]

    await message.answer("⏳ Gândesc...")

    try:
        response = await ask_openai(message.text)

        if not response:
            await message.answer("❌ OpenAI nu a putut răspunde. Încearcă din nou!")
            return

        await message.answer(f"💬 **Răspuns AI:**\n{response}")

        # Salvăm conversația în Bitrix24
        add_comment_to_deal(deal_id, f"**Întrebare:** {message.text}\n**Răspuns:** {response}")

    except Exception as e:
        await message.answer(f"❌ Eroare la procesarea cererii: {e}")


@dp.callback_query(F.data.startswith("contact_manager_"))
async def contact_manager_callback(callback: CallbackQuery):
    deal_id = callback.data.split("_")[2]
    user = await get_user(callback.from_user.id)

    if not user:
        await callback.message.answer("⚠️ Trebuie să te înregistrezi mai întâi.")
        await callback.answer()
        return

    notify_manager(
        deal_id=deal_id,
        user_name=user["name"],
        phone=user["phone"],
        email=user["email"]
    )

    await callback.message.answer("📩 Am notificat un manager! Vei fi contactat în curând.")
    await callback.answer()

@dp.callback_query(F.data.startswith("proceed_payment_"))
async def proceed_payment_callback(callback: CallbackQuery):
    await callback.message.answer("💳 Click pe link pentru a efectua plata: [Plată](https://your-payment-link.com)", parse_mode="Markdown")
    await callback.answer()

# Pornirea botului
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
