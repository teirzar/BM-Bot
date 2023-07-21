from aiogram import Bot, Dispatcher
from db import DBconnect
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from functions import get_token


# переменные для запуска бота
TOKEN = get_token()
storage = MemoryStorage()
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=storage)


# расположение файла с базой
src = "db/db_bot.db"
# подключение таблиц базы данных
users = DBconnect("users", src)
messages = DBconnect("messages", src)
orders = DBconnect("orders", src)
cafe = DBconnect("cafe", src)
types_base = DBconnect("types", src)
bonus = DBconnect("bonus", src)


START_MESSAGE = """
<b>BURGERMAKER</b>
    😀Рады вас видеть!😀
Ознакомьтесь с нашим меню,
закажите самые вкусные позиции!
    ! Вам начислено !
<b>50 приветственных бонусов</b>😉

<i>Спасибо</i>
"""

HELP_MESSAGE = """
Список доступных команд:

/start - начальное меню
/help - помощь
/menu - меню ресторана
/profile - профиль
/orders - прошлые заказы
/about - о нас
/call - позвонить нам
/settings - настройки, обратная связь

"""

ABOUT_MESSAGE = """<b>BURGERMAKER</b>

Время работы:
Понедельник-Четверг: с 11:00 до 20:45
Пятница: с 11:00 до 21:45
Суббота: с 11:00 до 20:45
Воскресенье: с 11:00 до 18:00

Адрес: <a href='https://yandex.ru/maps/-/CCUSUPHggB'>Ленинградская область, Всеволожский район, \
Агалатовское сельское поселение, массив Скотное, Шоссейная улица, 1</a>"""

