from aiogram import types
from config import users


# get telegram id
async def get_tg_id(message: types.Message | types.CallbackQuery) -> int:
    """Возвращает telegram id пользователя"""
    return int(message['from'].id)


# get user id
async def get_user_id(message: types.Message | types.CallbackQuery) -> int:
    """Возвращает id пользователя из базы данных"""
    return int(users.print_table('id', where=f"tg_id = {await get_tg_id(message)}")[0][0])


# get admins
async def get_admins() -> tuple:
    """Возвращает кортеж из администраторов бота, обращается к таблице users из базы данных"""
    admins = users.print_table('tg_id', where='status = 99')
    if admins:
        tpl_out = (el[0] for el in admins)
        return tuple(tpl_out)
    return tuple()
