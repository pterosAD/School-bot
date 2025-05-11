import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv
import os
from questions import questions

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

user_data = {}

def get_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("Да", callback_data="yes"),
        InlineKeyboardButton("Нет", callback_data="no")
    )
    return kb

@dp.message_handler(commands=["start"])
async def start_test(message: types.Message):
    user_data[message.from_user.id] = {"answers": [], "current_q": 0}
    await message.answer("Привет! Давайте начнем тест на личностные изменения.")
    await send_question(message.from_user.id)

async def send_question(user_id):
    data = user_data[user_id]
    if data["current_q"] < len(questions):
        q_text = questions[data["current_q"]]
        await bot.send_message(user_id, q_text, reply_markup=get_keyboard())
    else:
        score = data["answers"].count("yes")
        feedback = "Вы открыты для изменений!" if score >= 7 else "Возможно, стоит подумать о внутренней работе над собой."
        await bot.send_message(user_id, f"Результат теста: {feedback}")
        await bot.send_message(ADMIN_ID, f"Пользователь {user_id} прошёл тест. Балл: {score}/10")
        await bot.send_message(user_id, "Присоединяйтесь к нашему каналу: https://t.me/your_channel")

@dp.callback_query_handler(lambda c: c.data in ["yes", "no"])
async def process_answer(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_data[user_id]["answers"].append(callback_query.data)
    user_data[user_id]["current_q"] += 1
    await callback_query.answer()
    await send_question(user_id)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)