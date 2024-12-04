import aiohttp
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN, WEATHER_TOKEN

# Настройка логирования
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

async def get_weather(city_name: str) -> str:
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city_name,
        'appid': WEATHER_TOKEN,
        'units': 'metric',
        'lang': 'ru'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, params=params) as response:
            data = await response.json()

            if data.get('cod') != 200:
                return "Не удалось получить данные о погоде. Проверьте название города."

            city = data['name']
            weather_description = data['weather'][0]['description']
            temperature = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']

            return (f"Погода в {city}:\n"
                    f"{weather_description}\n"
                    f"Температура: {temperature}°C\n"
                    f"Ощущается как: {feels_like}°C\n"
                    f"Влажность: {humidity}%")

async def main():
    await dp.start_polling(bot)

@dp.message(Command(commands=['start']))
async def start(message: Message, state: FSMContext):
    await message.answer("Приветствую! Я покажу тебе погоду для любого города. Напиши название города")

@dp.message(Command(commands=['help']))
async def help(message: Message, state: FSMContext):
    await message.answer("Напишите название города, чтобы получить информацию о погоде.")

@dp.message()
async def send_weather(message: Message, state: FSMContext):
    city_name = message.text
    weather_info = await get_weather(city_name)
    await message.reply(weather_info, parse_mode=ParseMode.HTML)

if __name__ == "__main__":
    asyncio.run(main())