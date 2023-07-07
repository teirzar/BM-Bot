from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from config import bot, HELP_MESSAGE, START_MESSAGE, ABOUT_MESSAGE, users
from functions import add_log, get_tg_id, get_admins, get_user_id
from keyboards import kb_client_main_menu, kb_client_settings_menu, kb_client_menu_menu


# =======================================
#               MAIN MENU
# =======================================

async def cmd_client_start_menu(message: types.Message):
    """Стартовое меню, запись аккаунта в БД"""
    tg_id = await get_tg_id(message)
    if (tg_id, ) not in users.print_table('tg_id'):
        username, name = message["from"].username, message["from"].first_name
        text = f" Новый пользователь {name}! TG: {username} ID_{tg_id}"
        users.write('tg_id', 'username', 'name', values=f'{tg_id}, "{username}", "{name}"')
        await add_log(text)
        [await bot.send_message(admin, text) for admin in await get_admins()]
        return await bot.send_message(tg_id, START_MESSAGE, parse_mode='html', reply_markup=await kb_client_main_menu())
    await add_log(f"ID_{await get_user_id(message)} зашел в главное меню")
    return await bot.send_message(tg_id, "Главное меню", reply_markup=await kb_client_main_menu())

# =======================================
#              END MAIN MENU
# =======================================


# ====================== LOADING ======================
def register_handlers_client(dp: Dispatcher):
    """Регистрация хэндлеров"""
    dp.register_message_handler(cmd_client_start_menu, commands=['start'])
    dp.register_message_handler(cmd_client_start_menu, Text(equals='🏠 На главную'))
