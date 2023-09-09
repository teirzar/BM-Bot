from aiogram import types
from config import bot, users
from functions import get_order_list_text, get_basket, add_log, get_admins, get_tg_id


async def get_order_text(user_id, res):
    """Функция генерирует текст для админа о содержании заказа пользователя,
    res - tuple, в котором 3 переменные:
    price заказа, discount - скидка, lst - список товаров пользователя, order_id - id заказа в базе"""
    price, discount, lst, order_id = res
    text = f"Новый заказ ID_{order_id} от пользователя ID_{user_id}!\nСписок позиций:\n\n"
    text += await get_order_list_text(await get_basket(user_id, lst=lst))
    text += f"\nСумма заказа: {price}\nСкидка составила: {discount}"
    return text


def decor_private(func):
    """Декоратор для установки приватности команд"""
    async def wrapper(message: types.Message):
        tg_id = await get_tg_id(message)
        admins = await get_admins()
        if tg_id in admins:
            await add_log(f"TG_{tg_id} [успешный вход] [{func.__name__}]")
            await func(message)
        else:
            await add_log(f"TG_{tg_id} [неуспешно] {func.__name__}")
            await bot.send_message(tg_id, "Доступ закрыт.")
        return
    return wrapper


async def make_admin(data) -> str | int:
    """Функция проверки на корректность набора сообщения с ID админа и назначение нового админа"""
    if len(data) != 2:
        return "Неверный формат ввода.\nПример: /makeadmin 210189427"
    try:
        new_id = int(data[1])
    except ValueError:
        return "Неверный формат ввода! id должен состоять ТОЛЬКО из цифр!\nПример: /makeadmin 210189427"
    if (new_id, ) not in users.print_table('tg_id'):
        return "Данный пользователь не найден в системе!"
    users.update(f'status = 99', where=f'tg_id = {new_id}')
    return new_id
