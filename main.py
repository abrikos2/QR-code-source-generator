import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import FSInputFile, BufferedInputFile
from aiogram.filters import Command

from qrcodegenerator import QRCodeGenerator 

API_TOKEN = os.getenv('API_TOKEN')
dp = Dispatcher()
bot = Bot(API_TOKEN)
QR = QRCodeGenerator()



@dp.message(F.text, Command("start"))
async def start(message: types.Message):
    await bot.send_message(message.chat.id , 'Данный бот создан для презентации индивидуального проекта студента Грудзинский Даниил РПО 24/2. Для создания QR-кода следующеми сообщениями введите текст или ссылку который хотите превратить в QR-код')
@dp.message(F.text)
async def message(message: types.Message):
    await bot.send_photo (message.chat.id, BufferedInputFile(QR.generate(message.text, 'cc.png'), filename='image.png')) 
    await bot.send_message(message.chat.id, message.text)
async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=API_TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
