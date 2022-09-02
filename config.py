import requests
import datetime
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from email import message
from db import Database
from cgitb import text
from email import message

API_KEY = '5711390928:AAGEM1AgG3WrV0TL3Lsa273P5m0o0_zni5g'
open_weather_token = '5b423686873e6d56fcfaa17fe427eff5'

bot = Bot(token=API_KEY)
dp = Dispatcher(bot)
db = Database('databace.db')

@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    await message.reply("☁Привет!\n🏙 Напиши мне название города и я пришлю сводку погоды!\n\nПример:\nМосква или Moscow\n")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = ["Меню"]
    keyboard.add(*buttons)
    if not db.user_exists(message.from_user.id):#Если пользователь не существует 
        db.add_user(message.from_user.id)
        await bot.send_message(message.from_user.id, "")
    await message.answer("Для перехода в меню напишите 'Меню'\nИли воспользуйтесь кнопкой Меню", reply_markup=keyboard)

@dp.message_handler(commands="sendall")
async def sendall(message: types.Message):
    if message.from_user.id == 1471702705:
        text = message.text[9:]
        users = db.get_users()
        for row in users:
            try:
                await bot.send_message(row[0], text)
                if int(row[1]) != 1:
                    db.set_active(row[0], 1)
            except:
                db.set_active(row[0], 1)

    await bot.send_message(message.from_user.id, "Успешная рассылка")

@dp.message_handler(lambda message: message.text == "Меню")
async def without_puree(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="❗Подписка  на рассылку новостей", callback_data="podp"))
    keyboard.add(types.InlineKeyboardButton(text="❌Отписка от рассылки новостей", callback_data="podp2"))
    keyboard.add(types.InlineKeyboardButton(text="❓Информация", callback_data="info"))
    await message.answer("🟩Добро пожаловать в меню!", reply_markup=keyboard)

@dp.callback_query_handler(text="random_value")
async def send_random_value(call: types.CallbackQuery):

    buttons = [
        types.InlineKeyboardButton(text="🤖 GitHub бота", url="https://github.com/Ilya-Ivankov/BOT"),
        types.InlineKeyboardButton(text="✈ Telegram канал автора", url="https://t.me/ilya_ivankov"),
        types.InlineKeyboardButton(text="🏛 Сайт Мос. Политеха", url="https://mospolytech.ru/"),
        types.InlineKeyboardButton(text="🖥 ФИТ Мос. Политеха", url="https://fit.mospolytech.ru/"),
        types.InlineKeyboardButton(text="Назад", callback_data="info")  
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    await call.message.answer("🟩Ссылки", reply_markup=keyboard)

@dp.callback_query_handler(text="podp")
async def without_puree(call: types.CallbackQuery):
    buttons = [
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    await call.message.answer("Подписка успешно оформленна, спасибо за подписку! ", reply_markup=keyboard)
    await call.message.answer("Получаей самую важную информацию первым!", reply_markup=keyboard)

@dp.callback_query_handler(text="podp2")
async def without_puree(call: types.CallbackQuery):
    db.del_user(call.message.from_user.id)
    buttons = [
        types.InlineKeyboardButton(text="✈ Telegram канал автора", url="https://t.me/ilya_ivankov"),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    await call.message.answer("Отписка оформлена")
    await call.message.answer("Отпиши автору проекта, что тебе не понравилось", reply_markup=keyboard)

@dp.callback_query_handler(text="info")
async def without_puree(call: types.CallbackQuery):
    buttons = [
        types.InlineKeyboardButton(text="Ссылки", callback_data="random_value"),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    await call.message.answer("✅Данный бот был создан в учебных целях студентом Московского Политеха Иваньковым И. (201-363)\n❇Основное применнение данного бота, получение информации о погоде в интресующим Вас городе \n✳Версия бота: v 0.0.1", reply_markup=keyboard)      

@dp.message_handler()
async def get_weather(message: types.Message):
    code_to_smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Drizzle": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B"
    }
    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={open_weather_token}&units=metric"
        )
        data = r.json()

        city = data["name"]
        cur_weather = data["main"]["temp"]

        weather_description = data["weather"][0]["main"]
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = "♻"

        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"]).strftime('%H:%M')
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"]).strftime('%H:%M')
        length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(data["sys"]["sunrise"])

        await message.reply(f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n"
              f"Погода в городе: {city}\nТемпература: {cur_weather}C° {wd}\n"
              f"Влажность: {humidity}%\nДавление: {pressure} мм.рт.ст\nВетер: {wind} м/с\n"
              f"Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\nПродолжительность дня: {length_of_the_day}\n"
              f"***Хорошего дня!*** "
              )

    except:
        await message.reply("\U00002620 Проверьте название города \U00002620")

if __name__ == '__main__':
    executor.start_polling(dp)

    