import logging
import csv
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
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
    {"key": "child_name", "text": "Введите ФИО ребенка:"},
    {"key": "birth_date", "text": "Введите дату рождения:"},
    {"key": "handedness", "text": "Ребенок правша, левша или амбидекстр?"},
    {"key": "bilingual", "text": "Есть ли в семье двуязычие? (да/нет)"},
    {"key": "diseases", "text": "Перенесённые заболевания, медикаментозное лечение:"},
    {"key": "specialists", "text": "Стояли или стоите на учёте у узких специалистов:"},
    {"key": "logoped", "text": "Посещали раньше логопеда или нет:"},
    {"key": "logoped_exercises", "text": "Если да, какие упражнения выполняются:"},
    {"key": "siblings", "text": "Есть ли ещё дети в семье, возраст:"},
    {"key": "mother_name", "text": "ФИО матери:"},
    {"key": "mother_age", "text": "Возраст матери на время рождения ребёнка:"},
    {"key": "mother_inherited_diseases", "text": "Наследственные заболевания (мать):"},
    {"key": "mother_speech_defects", "text": "Дефекты речи, неправильный прикус у мамы (отсутствуют-присутствуют; если есть, какие):"},
    {"key": "father_name", "text": "ФИО отца:"},
    {"key": "father_age", "text": "Возраст отца на время рождения ребёнка:"},
    {"key": "father_inherited_diseases", "text": "Наследственные заболевания (отец):"},
    {"key": "father_speech_defects", "text": "Дефекты речи, неправильный прикус у папы (отсутствуют-присутствуют; если есть, какие):"},
    {"key": "pregnancy_term", "text": "На каком сроке были роды:"},
    {"key": "pregnancy_issues", "text": "Травмы, болезни, токсикоз, угроза прерывания беременности:"},
    {"key": "birth_type", "text": "Досрочные, срочные, быстрые, обезвоженные:"},
    {"key": "stimulation", "text": "Стимуляция:"},
    {"key": "asphyxia", "text": "Асфиксия (синяя, красная, белая):"},
    {"key": "birth_injuries", "text": "Обвитие, травмы, гематомы:"},
    {"key": "resus_factor", "text": "Резус-фактор (мама (+ или -); ребёнок (+ или -)):"},
    {"key": "birth_weight", "text": "Вес и рост при рождении:"},
    {"key": "feeding_type", "text": "Активное сосание, отказ от груди:"},
    {"key": "feeding_problems", "text": "Поперхивания во время сосания, чрезмерное срыгивание:"},
    {"key": "pacifier", "text": "Сосал ли ребёнок соску, если да, то до какого возраста:"},
    {"key": "early_head_control", "text": "Держал(а) голову (в 1,5-2 мес.):"},
    {"key": "early_sitting", "text": "Сидел(а) (в 6 мес.):"},
    {"key": "early_crawling", "text": "Ползал(а) (в 7-8 мес.):"},
    {"key": "early_walking", "text": "Ходил(а) (к 1 году):"},
    {"key": "first_teeth", "text": "Появление первых зубов (в 6-8 мес.):"},
    {"key": "teeth_count_1_year", "text": "Количество зубов к 1 году:"},
    {"key": "motor_development", "text": "Двигательно беспокоен(йна):"},
    {"key": "crying", "text": "Криклив(а):"},
    {"key": "sleep_problems", "text": "С трудом засыпал (ла):"},
    {"key": "sleep_disturbances", "text": "Беспокойный и короткий сон:"},
    {"key": "sluggishness", "text": "Заторможенный(ая), вялый(ая), не реагировал на окружающих:"},
    {"key": "gurgling", "text": "Время появления гуления (2-3 мес.):"},
    {"key": "babbling", "text": "Время появления лепета (4-6 мес.):"},
    {"key": "first_words", "text": "Время появления первых слов (до 1 года):"},
    {"key": "first_phrase", "text": "Первая фраза (1,5-2 года):"},
    {"key": "speech_delay", "text": "Прерывалось ли речевое развитие:"},
    {"key": "parent_comments", "text": "Замечания, жалобы родителей на речевое развитие ребёнка:"},
]

# Функция для сохранения данных в CSV
def save_to_csv(user_id, user_data):
    file_name = 'responses.csv'
    
    # Проверка на существование файла. Если файл не существует — создаем заголовки
    file_exists = False
    try:
        with open(file_name, 'r'):
            file_exists = True
    except FileNotFoundError:
        pass

    with open(file_name, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Если файл не существует, записываем заголовки
        if not file_exists:
            writer.writerow(['User ID', 'ФИО ребенка', 'Дата рождения', 'Ребенок правша/левша', 'Двуязычие', 
                             'Перенесенные заболевания', 'Стояли ли на учете у узких специалистов', 'Посещали логопеда',
                             'Упражнения логопеда', 'Есть ли дети в семье', 'ФИО матери', 'Возраст матери', 'Наследственные заболевания (мать)', 
                             'Дефекты речи у мамы', 'ФИО отца', 'Возраст отца', 'Наследственные заболевания (отец)', 
                             'Дефекты речи у папы', 'На каком сроке были роды', 'Проблемы во время беременности', 'Родовые травмы', 
                             'Стимуляция родов', 'Асфиксия', 'Обвитие, травмы', 'Резус-фактор', 'Вес и рост при рождении',
                             'Активное сосание', 'Отказ от груди', 'Проблемы с сосанием', 'Соска', 'Развитие моторики',
                             'Речь в раннем возрасте', 'Сон', 'Замечания родителей'])

        # Запись данных в CSV
        writer.writerow([user_id] + [user_data.get(q['key'], '') for q in QUESTIONS])

# Создание бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

users_data = {}
current_question = {}

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

# Запуск бота
async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
