from aiogram import types
from config import users


# get telegram id
async def get_tg_id(message: types.Message | types.CallbackQuery) -> int:
    """Возвращает ТГ айди"""
    return int(message['from'].id)


# get user id
async def get_user_id(message: types.Message | types.CallbackQuery) -> int:
    """Возвращает id пользователя из базы данных"""
    return int(users.print_table('id', where=f"tg_id = {await get_tg_id(message)}")[0][0])

