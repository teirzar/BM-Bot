from aiogram import types
from config import bot, users, cafe, orders, types_base, bonus, messages
from functions import get_order_list_text, get_basket, add_log, get_tg_id, get_owner, get_time, cancel_order


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
    comment = orders.print_table('comment', where=f'id = {order_id}')[0][0]
    text = f"Новый заказ ID_{order_id} от пользователя ID_{user_id}!\nСписок позиций:\n\n"
    text += await get_order_list_text(await get_basket(user_id, lst=lst))
    text += f"\nСумма заказа: {price}\nСкидка составила: {discount}\n\nКомментарий к заказу:\n{comment}"
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
            await add_log(f"TG_{tg_id} [неуспешно] [{func.__name__}]")
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


async def admin_order_work(tg_id, order_id, cmd) -> tuple | str:
    """Функция, для обработки заказов и работой с ними, переключение статусов заказа"""
    order_data = orders.print_table('date_order', 'date_accept', 'date_complete', 'date_end', 'user_id', 'price',
                                    where=f'id = {order_id}')
    date_order, date_accept, date_complete, date_end, user_id, price = order_data[0]
    user_tg = users.print_table('tg_id', where=f'id = {user_id}')[0][0]
    date_now = await get_time()

    if date_end:
        return "Заказ был завершен или отменен."

    match cmd:

        case "accept":
            if any([date_accept, date_complete, date_end]):
                return "Не удалось принять заказ, он уже был принят ранее."
            new_date, new_status = "date_accept", 2
            text_for_user = "Ваш заказ начали готовить! Ожидание займет не менее 10 минут!"

        case "complete":
            if any([date_complete, date_end]):
                return "Не удалось отметить готовность заказа. Заказ уже готов."
            new_date, new_status = "date_complete", 3
            text_for_user = "Ваш заказ готов! Спешите получить его, пока не остыл! 😊😊😊\nПриятного аппетита!"

        case "cancel" | "unsuccessfully":
            new_date, new_status = "date_end", 5
            if cmd == "cancel":
                if date_complete:
                    return "Не удалось отменить заказ. Заказ уже готов."
                text_for_user = await cancel_order(order_id, admin_id=tg_id)
                return f"Заказ № {order_id} отменен администратором TG_{tg_id}", text_for_user, user_tg
            text_for_user = "Вы не забрали свой заказ в заведении. Заказ отменен. Бонусы возвращены не будут."

        case "successfully":
            new_date, new_status = "date_end", 4
            user_status = users.print_table('status', where=f'id = {user_id}')[0][0]
            discount = bonus.print_table('discount', where=f'status = {user_status}')[0][0] if user_status != 99 else 20
            cashback = int((price/100)*discount)
            users.update(f'bonus = bonus + {cashback}, total_price = total_price + {price}', where=f'id = {user_id}')
            text_for_user = f"Заказ успешно завершен!\nСпасибо за заказ!\nНа ваш счет зачислено {cashback} бонусов."
            if user_status not in (3, 99):
                current_total_price = users.print_table('total_price', where=f'id = {user_id}')[0][0]
                next_total_price, next_discount, next_name = bonus.print_table('price', 'discount', 'name',
                                                                               where=f'status = {user_status + 1}')[0]
                if current_total_price >= next_total_price:
                    users.update(f'status = {user_status + 1}', where=f'id = {user_id}')
                    text_for_user += f'\n\nПоздравляем!\nВаш статус обновлен до [{next_name}]!\n' \
                                     f'Теперь ваш уровень кэшбека составляет {next_discount}% от заказа! 😊\n' \
                                     f'Спасибо, что остаетесь с нами!'

    name_status = types_base.print_table('name', where=f'base = "orders" and typ = {new_status}')[0][0]
    orders.update(f'status = {new_status}, {new_date} = "{date_now}", adm_id = {tg_id}', where=f'id = {order_id}')
    return f"Статус заказа ID_{order_id} успешно обновлен до статуса [{name_status}]", text_for_user, user_tg


async def get_cafe_column_names() -> dict:
    """Функция предназначена для русифицированного вывода названий колонок из таблицы cafe"""
    return dict(types_base.print_table('typ', 'name', where='base = "cafe_column"'))


async def get_current_food_value(food_id, column):
    """Функция по возврату конкретного значения блюда из базы, по id объекта и названию колонки"""
    return cafe.print_table(column, where=f'id = {food_id}')[0][0]


def inline_private(func):
    """Декоратор для установки приватности inline-команд"""
    async def wrapper(callback: types.CallbackQuery):
        tg_id = await get_tg_id(callback)
        if tg_id not in await get_admins():
            await add_log(f'TG_{tg_id} [неуспешно] [{func.__name__}]')
            await callback.message.delete()
            return await callback.answer("Данная функция доступна только администраторам.", show_alert=True)
        await func(callback)
        return
    return wrapper


async def get_current_messages_admin() -> tuple:
    """Функция, возвращающая список всех неотвеченных сообщений от пользователей"""
    return messages.print_table('id', 'tg_id', 'time', where=f'adm_id is NULL')


async def get_text_message(message_id) -> str:
    """Функция предназначена для генерации и вывода текста сообщения от пользователя администратору"""
    tg_id, message, date = messages.print_table('tg_id', 'message', 'time', where=f'id = {message_id}')[0]
    user_id, sep = users.print_table('id', where=f'tg_id = {tg_id}')[0][0], f'\n{"=" * 15}\n'
    return f'Сообщение ID_{message_id}.\nОт: ID_{user_id} (TG_{tg_id})\n{sep}Text: <{message}>{sep}\nДата: {date}'


async def is_read(message_id) -> bool:
    """Возвращает булевое значение True если сообщение прочитано, и False если не прочитано"""
    return bool(messages.print_table('adm_id', where=f'id = {message_id}')[0][0])


async def make_message_read(tg_id, message_id) -> str | None:
    """Функция для отметки о прочтении сообщения, возвращает строку,
    если сообщение уже было прочитано или на него был дан ответ"""
    if await is_read(message_id):
        return "Сообщение уже было прочитано, или на него был дан ответ."
    now = await get_time()
    messages.update(f'answer_time = "{now}", adm_id = {tg_id}', where=f'id = {message_id}')
    return


async def send_to_admins(text, kb=None):
    """Функция для отправки технологичского текста админитрации в личные сообщения от бота"""
    [await bot.send_message(admin, text, reply_markup=kb) for admin in await get_admins()]
