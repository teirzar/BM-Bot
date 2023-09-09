from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from config import bot
from functions import decor_private, add_log, make_admin


# =======================================
#                 OTHER
# =======================================

@decor_private
async def cmd_make_admin(message: types.Message):
    """Функция для записи нового админа"""
    data = message.text.split()
    res = await make_admin(data)
    await add_log(f'TG_{message.from_user.id} пытается назначить администратора командой [{message.text}]')
    if type(res) == str:
        return await message.answer(res)
    await add_log(f"TG_{message.from_user.id} назначил администратора TG_{res}")
    await bot.send_message(res, "Вы назначены администратором в боте BURGERMAKER.\nПоздравляем!\nАдминка: /admin")
    await message.answer("Админ назначен")


# =======================================
#               END OTHER
# =======================================

# ====================== LOADING ======================
def register_handlers_admin(dp: Dispatcher):
    """Регистрация хэндлеров"""
    dp.register_message_handler(cmd_make_admin, commands=['makeadmin'])
