import logging
import csv
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import os
from aiohttp import web
from config import API_TOKEN

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Создание бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# Данные анкеты
users_data = {}
current_question = {}
QUESTIONS = [
    # Ваши вопросы здесь...
]

# Функция для сохранения данных в CSV
def save_to_csv(user_id, user_data):
    # Сохранение данных в CSV...
    pass

# Обработка команды /start
@router.message(Command("start"))
async def start(message: Message):
    user_id = message.from_user.id
    current_question[user_id] = 0
    await message.answer("Здравствуйте! Давайте начнем заполнение анкеты.")
    await ask_next_question(user_id, message)

# Отправка следующего вопроса
async def ask_next_question(user_id, message: Message):
    if current_question[user_id] < len(QUESTIONS):
        question = QUESTIONS[current_question[user_id]]
        await message.answer(question['text'])
    else:
        await message.answer("Спасибо! Анкета заполнена.")
        print(users_data[user_id])

# Обработка ответов
@router.message()
async def handle_input(message: Message):
    user_id = message.from_user.id
    logging.info(f"Received message from {user_id}: {message.text}")

    if user_id in current_question:
        question = QUESTIONS[current_question[user_id]]
        if user_id not in users_data:
            users_data[user_id] = {}

        # Сохраняем ответ пользователя в словарь
        users_data[user_id][question['key']] = message.text
        current_question[user_id] += 1
        
        # Сохраняем данные в CSV
        save_to_csv(user_id, users_data[user_id])
        
        await ask_next_question(user_id, message)
    else:
        await message.answer("Введите /start для начала анкеты.")

# Веб-сервер для Render
async def handle(request):
    return web.Response(text="Бот работает!")

# Установка webhook для Telegram
async def set_webhook():
    webhook_url = os.getenv("WEBHOOK_URL")  # Убедитесь, что у вас есть URL на Render
    await bot.set_webhook(f'{webhook_url}/webhook')

# Запуск бота и веб-сервера
async def main():
    dp.include_router(router)
    
    # Настройка webhook
    await set_webhook()

    # Веб-сервер для обработки webhook
    app = web.Application()
    app.add_routes([web.post('/webhook', handle)])  # Обработка запросов на /webhook
    
    # Устанавливаем порт для Render
    port = int(os.environ.get('PORT', 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

if __name__ == "__main__":
    asyncio.run(main())

