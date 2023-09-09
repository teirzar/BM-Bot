from aiogram import types
from config import bot, users, cafe, orders
from functions import get_order_list_text, get_basket, add_log, get_tg_id, get_owner


async def get_admins() -> tuple:
    """Возвращает кортеж из администраторов бота, обращается к таблице users из базы данных"""
    admins = users.print_table('tg_id', where='status = 99')
    if admins:
        tpl_out = (el[0] for el in admins)
        return tuple(tpl_out)
    return tuple()


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


async def set_admin(data, delete=False) -> str | int:
    """Функция проверки на корректность набора сообщения с ID админа и назначение нового админа"""
    if len(data) != 2:
        return f"Неверный формат ввода.\nПример: {'/deleteadmin' if delete else '/makeadmin'} 210189427"
    try:
        new_id = int(data[1])
    except ValueError:
        return f"Неверный формат ввода! id должен состоять ТОЛЬКО из цифр!\n" \
               f"Пример: {'/deleteadmin' if delete else '/makeadmin'} 210189427"
    if (new_id, ) not in users.print_table('tg_id'):
        return "Данный пользователь не найден в системе!"
    if delete:
        if new_id not in await get_admins():
            return "Пользователь не является администратором"
        users.update(f'status = 2', where=f'tg_id = {new_id}')
        return new_id
    if new_id in await get_admins():
        return "Данный пользователь уже администратор!"
    users.update(f'status = 99', where=f'tg_id = {new_id}')
    return new_id


async def show_admins() -> str:
    """Функция для вывода в текстовом формате информации об администраторах"""
    admins = users.print_table('id', 'tg_id', 'username', 'name', 'phone', where='status = 99')
    text = ""
    for i, t, u, n, p in admins:
        text += f"ID_{i}: Tg - {t}\nUsername - {u}\nИмя - {n}\nТелефон - {p}\n\n"
    return text


async def give_me_admin() -> None:
    """Функция для того чтобы владелец мог выдать себе админку"""
    users.update(f'status = 99', where=f'tg_id = {get_owner()}')
    return


async def status_changer(changed_id, is_notification=False) -> int:
    """Функция для изменения одного значения в базе с 0 на 1 и наоборот"""
    base = users if is_notification else cafe
    column = 'notification' if is_notification else 'status'
    current = base.print_table(column, where=f'id = {changed_id}')[0][0]
    base.update(f'{column} = {int(not current)}', where=f'id = {changed_id}')
    return int(not current)


async def get_current_orders_admin() -> tuple:
    """Функция, возвращающая список всех активных заказов"""
    return orders.print_table('id', 'user_id', 'price', 'status', where=f'status in (1, 2, 3)')
