import asyncio
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = os.environ.get("BOT_TOKEN", "ВАШ_ТОКЕН_ИЗ_BOTFATHER")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "ВАШ_TELEGRAM_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def get_faq_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="⏱ Терміни друку", callback_data="faq_time")
    builder.button(text="🧵 Матеріали (PLA, PETG, ABS)", callback_data="faq_materials")
    builder.button(text="📦 Доставка та оплата", callback_data="faq_delivery")
    builder.button(text="💬 Написати оператору", callback_data="to_operator")
    builder.adjust(1)
    return builder.as_markup()

def get_back_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="◀️ Назад до меню", callback_data="back_to_menu")
    return builder.as_markup()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "Вітаємо у службі підтримки **Renat 3D Kyiv Shop**! 🛠️\n\n"
        "Оберіть запитання нижче або натисніть «Написати оператору»:",
        reply_markup=get_faq_keyboard()
    )

@dp.callback_query(F.data.startswith("faq_"))
async def process_faq(callback: types.CallbackQuery):
    data = callback.data
    answer_text = ""
    if data == "faq_time":
        answer_text = "⏱ **Терміни виготовлення:**\n• Швидке замовлення: 1–2 дні.\n• Звичайне замовлення: 1–4 дні."
    elif data == "faq_materials":
        answer_text = "🧵 **Матеріали:**\n• **PLA** — іграшки, фігурки, декор.\n• **PETG** — міцні деталі, автоаксесуари.\n• **ABS** — термостійкі корпуси."
    elif data == "faq_delivery":
        answer_text = "📦 **Доставка та оплата:**\n• Оплата на картку ПриватБанку.\n• Доставка Новою Поштою за тарифами перевізника."
        
    await callback.message.edit_text(answer_text, reply_markup=get_back_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "back_to_menu")
async def back_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Головне меню підтримки:",
        reply_markup=get_faq_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "to_operator")
async def switch_to_operator(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "💬 Ви переведені на оператора.\n"
        "Напишіть ваше запитання або надішліть файл, і ми відповімо найближчим часом!"
    )
    await callback.answer()

@dp.message(F.chat.id != ADMIN_ID)
async def forward_to_admin(message: types.Message):
    await message.forward(chat_id=ADMIN_ID)
    await message.answer("✅ Ваше повідомлення надіслано менеджеру. Очікуйте відповіді!")

@dp.message(F.chat.id == ADMIN_ID, F.reply_to_message)
async def reply_to_user(message: types.Message):
    if message.reply_to_message.forward_from:
        user_id = message.reply_to_message.forward_from.id
        if message.text:
            await bot.send_message(chat_id=user_id, text=message.text)
        elif message.photo:
            await bot.send_photo(chat_id=user_id, photo=message.photo[-1].file_id, caption=message.caption)
        elif message.document:
            await bot.send_document(chat_id=user_id, document=message.document.file_id, caption=message.caption)
        await message.answer("✅ Відповідь надіслано клієнту.")
    else:
        await message.answer("⚠️ Відповідайте саме на переслане повідомлення клієнта.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
