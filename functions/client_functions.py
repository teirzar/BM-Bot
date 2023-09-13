from aiogram import types
from config import users, bonus, types_base, cafe, orders
from functions import get_time, add_log


async def get_tg_id(message: types.Message | types.CallbackQuery) -> int:
    """Возвращает telegram id пользователя"""
    return int(message['from'].id)


async def get_user_id(message: types.Message | types.CallbackQuery) -> int:
    """Возвращает id пользователя из базы данных"""
    return int(users.print_table('id', where=f"tg_id = {await get_tg_id(message)}")[0][0])


async def get_profile_text(user_id) -> str:
    """Возвращает информацию о пользователе в виде текста.
    Необходимо для функции 'Профиль инфо'. """
    users_dict = dict(zip(users.names(), *users.print_table(where=f"id = {user_id}")))
    bonus_dic = dict(bonus.print_table('name', 'price'))
    status = list(bonus_dic.keys())
    total_prices = list(bonus_dic.values())
    need_money = None
    if users_dict['status'] not in (3, 99):
        need_money = total_prices[users_dict['status'] + 1] - users_dict['total_price']
    next_status = "\n<i>До статуса '" + status[users_dict['status']+1] + f"': {need_money}р.</i>" if need_money else ''
    text = f"""<b>Ваш профиль</b>\n
    🆔 ID: {users_dict['id']}
    📇 Имя: {users_dict['name']}
    📱 Телефон: {users_dict['phone'] if users_dict['phone'] else "Укажите телефон в настройках!"}
    💰 Бонусы: {users_dict['bonus']}
    😎 Статус: {status[users_dict['status']] if users_dict['status'] != 99 else 'ADMIN'}{next_status}
    🔔 Уведомления: {"вкл." if users_dict['notification'] else "выкл."}
    \nИзменить данные можно в\n⚙ Настройках (/settings)"""
    return text


async def get_prev_orders(user_id, tg_id) -> str:
    """Возвращает текст о последних заказах пользователя, если его нет, возвращает текст о том, что список пуст.
    Необходимо для функции 'Мои заказы' """
    user_orders, total_price = users.print_table('orders', 'total_price', where=f'id = {user_id}')[0]
    if not user_orders:
        return "У вас нет ни одного заказа."
    text = f"У вас {len(user_orders.split())} заказов на общую сумму {total_price} руб.\n"
    current_order = orders.print_table('body', where=f'user_id = {user_id} and status = 0')
    if current_order and current_order[0][0]:
        text += f'\nНа данный момент товары ' \
                f'{await get_text_basket(tg_id, user_id, full=True)}'
    text += f"\nНажмите на интересующий Вас заказ, чтобы получить информацию о нем.\n\nПоследние 20 заказов:"
    return text


async def get_type_food_id(text) -> int:
    """Функция возвращает ID типа товарной позиции,
    для дальнейшего вызова соответствующего инлайна по запросу пользователя"""
    food_type = types_base.print_table('typ', where=f'base = "cafe" and name = "{text[1:].strip()}"')
    return food_type[0][0]


async def get_orders(user_id) -> str:
    """Возвращает строку с ID заказов пользователя"""
    user_orders = users.print_table('orders', where=f'id = {user_id}')
    return user_orders[0][0] if user_orders and user_orders[0][0] else ""


async def check_order(income_id, is_user_id=False):
    """Функция проверяет, есть ли заказ в базе, и если его нет, то создает заказ со статусом "В корзине",
    также попутно внося его в список заказов в базе данных пользователей"""
    user_id = income_id if is_user_id else users.print_table('id', where=f'tg_id = {income_id}')[0][0]
    if (user_id, ) not in orders.print_table('user_id', where=f'status = 0'):
        orders.write('user_id', 'body', 'date_start', 'status', values=f'{user_id}, "", "{await get_time()}", 0')
        order_id = orders.print_table('id', where=f'status = 0 and user_id = {user_id}')[0][0]
        current_orders = users.print_table('orders', where=f'id = {user_id}')[0][0]
        current_orders = f'{current_orders} {order_id}' if current_orders else order_id
        users.update(f'orders = "{current_orders}"', where=f'id = {user_id}')


async def get_food_kb_info(food_id) -> tuple:
    """Возвращает кортеж данных, необходимых для функционирования клавиатуры карточки товара.
    Содержит информацию о лайках, дизлайках на блюде, тип блюда"""
    typ, dislike, like = cafe.print_table('type', 'dislikes', 'likes', where=f'id = {food_id}')[0]
    dislike, like = len(dislike.split()), len(like.split())

    return typ, dislike, like


async def get_food_text(food_id) -> tuple:
    """Функция, предназначенная для вывода текста о товаре и ссылки на картинку в виде кортежа"""
    name, caption, composition, weight, price, image, type_food = \
        cafe.print_table('name', 'caption', 'composition', 'weight', 'price', 'image', 'type',
                         where=f'id = {food_id}')[0]
    pt = "гр" if type_food != 50 else "мл"
    text = f"<b>{name}\n{weight} {pt}., {price}руб.</b>\n\nОписание:\n{caption}\n\nСостав:\n{composition}"
    return text, image


async def get_basket(user_id, lst=None):
    """Возвращает корзину пользователя в виде словаря, где ключ - id блюда, а значение - количество товарных позиций"""
    await check_order(user_id, is_user_id=True)
    if not lst:
        lst = orders.print_table('body', where=f'user_id = {user_id} and status = 0')[0][0]
    basket = {el.split(":")[0]: int(el.split(":")[1]) for el in lst.split()}
    return basket


async def set_order(user_id, food_id, cmd) -> str | int:
    """Функция для изменения состояния заказа в корзине, выбор действия с товаром и реализация действия"""
    await check_order(user_id, is_user_id=True)

    order_id, current_lst = orders.print_table('id', 'body', where=f'user_id = {user_id} and status = 0')[0]
    current_basket = await get_basket(user_id, current_lst) if current_lst else {}

    match cmd:
        case "plus":
            if food_id not in current_basket:
                if len(current_basket) > 11:
                    return "Нельзя одновременно добавить более 12 различных товаров!"
                new_food = f"{current_lst} {food_id}:1"
                orders.update(f'body = "{new_food.strip()}"', where=f'id = {order_id}')
                return 1
            if current_basket[food_id] + 1 > 15:
                return "Нельзя одновременно добавить более 15 порций одного блюда!"
            current_basket[food_id] += 1
        case "minus" | "delete":
            if food_id not in current_basket:
                return "Товар отсутствует в корзине!"
            if cmd == "delete" or not current_basket[food_id] - 1:
                current_basket.pop(food_id)
            else:
                current_basket[food_id] -= 1

    orders.update(f'body = "{" ".join([f"{f}:{c}" for f, c in current_basket.items()]).strip()}"',
                  where=f'id = {order_id}')
    return current_basket.get(food_id, 0)


async def get_count(tg_id, current_id=None) -> tuple:
    """Функция для того, чтобы узнать какое количество конкретных позиций у пользователя в заказе,
    а так же стоимость и количество ВСЕХ товаров в корзине"""
    user_id = users.print_table('id', where=f'tg_id = {tg_id}')[0][0]

    await check_order(tg_id)

    current_lst = orders.print_table('body', where=f'user_id = {user_id} and status = 0')[0][0]
    basket = await get_basket(user_id, current_lst)
    food_count = 0
    if current_id and str(current_id) in basket:
        food_count = basket[str(current_id)]
    total_price = sum([cafe.print_table('price', where=f'id = {k}')[0][0] * int(v) for k, v in basket.items()])
    basket_count = sum(basket.values())
    return basket_count, total_price, food_count


async def clear_basket(user_id) -> str | int:
    """Функция для полной очистки корзины"""
    lst = orders.print_table('body', where=f'user_id = {user_id} and status = 0')[0][0]
    if lst:
        orders.update('body = ""', where=f'user_id = {user_id} and status = 0')
        return "Корзина была очищена!"
    return 0


async def set_rating(food_id, user_id, cmd) -> str | int:
    """Функция для установки лайков и дизлайков на блюдах"""
    altcmd = "dislikes" if cmd == "like" else "likes"
    lst, altlst = cafe.print_table(f'{cmd}s', altcmd, where=f'id = {food_id}')[0]
    if str(user_id) in lst.split():
        return f"Вы уже ставили {cmd} этому блюду!"

    new_lst = (lst + " " + str(user_id)).strip()
    if str(user_id) in altlst.split():
        altlst = altlst.split()
        altlst.remove(str(user_id))
        new_altlst = " ".join(altlst) if len(altlst) else ""
        cafe.update(f'{altcmd} = "{new_altlst}"', where=f'id = {food_id}')

    cafe.update(f'{cmd}s = "{new_lst}"', where=f'id = {food_id}')
    return 0


async def get_order_list_text(basket):
    """Функция для вывода текста ТОЛЬКО состава заказа, количество позиций и их цена"""
    names = {i: k for i, *k in cafe.print_table('id', 'name', 'price')}
    text = ""
    for i, count in basket.items():
        text += f"{names[int(i)][0]} - {count} шт. ({names[int(i)][1] * count} руб.)\n"
    return text


async def get_text_basket(tg_id, user_id, full=False) -> str:
    """Функция для генерации и возврата строки с информацией о заполненности корзины пользователя"""
    basket = await get_basket(user_id)
    basket_count, total_price, food_count = await get_count(tg_id)
    discount = await get_current_discount(user_id)
    text = f"в Вашей корзине:\n{basket_count} товара(-ов) на сумму {total_price} руб." \
        if len(basket) else "Ваша корзина пуста."
    text += f" (с учетом скидки цена: {total_price - discount} руб.)\n\n" if discount else "\n\n"
    if full:
        text += await get_order_list_text(basket)
    return text


async def get_user_bonus(user_id) -> int:
    """Функция возвращает значение бонусного баланса пользователя"""
    return users.print_table('bonus', where=f'id = {user_id}')[0][0]


async def get_user_status(user_id) -> tuple | str:
    """Функция возвращает текущий уровень кэшбека и статус пользователя"""
    status = users.print_table('status', where=f'id = {user_id}')[0][0]
    if status == 99:
        return "Админ не может совершать заказ!"
    discount, status_name = bonus.print_table("discount", "name", where=f'status = {status}')[0]
    return discount, status_name


async def get_current_discount(user_id) -> int:
    """Возвращает текущую скидку на заказе"""
    return orders.print_table('bonus', where=f'user_id = {user_id} and status = 0')[0][0]


async def set_order_price(tg_id, user_id) -> int:
    """Функция, необходимая для записи стоимости заказа в базу данных"""
    basket_count, total_price, food_count = await get_count(tg_id)
    orders.update(f'price = {total_price}', where=f'user_id = {user_id} and status = 0')
    return total_price


async def is_bonus_activated(user_id) -> bool | str:
    """Функция проверяет, активирован ли бонус на текущем заказе"""
    await check_order(user_id, is_user_id=True)
    try:
        return orders.print_table('bonus', where=f'user_id = {user_id} and status = 0')[0][0]
    except IndexError:
        return "Ваша корзина пуста!"


async def update_user_bonus(user_id) -> tuple | str:
    """Функция списывает бонусы пользователя, применяет скидку к заказу"""
    if not await get_basket(user_id):
        return "В корзине нет товаров!"
    tg_id, current_discount = users.print_table('tg_id', 'bonus', where=f'id = {user_id}')[0]
    order_price = await set_order_price(tg_id, user_id)
    check_price = order_price >= current_discount
    user_bonus = 0 if check_price else current_discount - order_price
    new_price = order_price - current_discount if check_price else 0
    current_discount = current_discount if check_price else order_price

    users.update(f'bonus = {user_bonus}', where=f'id = {user_id}')
    orders.update(f'price = {new_price}, bonus = {current_discount}', where=f'user_id = {user_id} and status = 0')

    return new_price, user_bonus, current_discount


async def make_purchase(user_id, tg_id) -> str | tuple:
    """Функция, активируемая при нажатии на подтверждение заказа, покупка товара"""
    await check_order(user_id, is_user_id=True)
    lst = orders.print_table('body', where=f'user_id = {user_id} and status = 0')[0][0]
    lst_status_1 = orders.print_table('id', where=f'user_id = {user_id} and status = 1')
    if len(lst_status_1) > 2:
        return "Нельзя создавать более 3 активных заказов! Дождитесь подтверждения от заведения!"
    if not lst:
        return "В Вашей корзине нет товаров!"
    order_id = orders.print_table('id', where=f'user_id = {user_id} and status = 0')[0][0]
    basket_count, total_price, food_count = await get_count(tg_id)
    discount = await get_current_discount(user_id)
    date = await get_time()
    orders.update(f'status = 1, price = {total_price - discount}, date_order = "{date}"',
                  where=f'user_id = {user_id} and status = 0')
    return total_price - discount, discount, lst, order_id


async def cancel_order(order_id, admin_id=None) -> None | str:
    """Функция для отмены заказа и генерации текста сообщения при отмене"""
    status = await get_order_status(order_id)
    if status not in (1, 2):
        return
    date = await get_time()
    user_id, discount = orders.print_table('user_id', 'bonus', where=f'id = {order_id}')[0]
    cancel_text = f"Ваш заказ № {order_id} был отменён"
    if status == 1 or admin_id:
        orders.update(f'date_end = "{date}", {f"adm_id = {admin_id}, " if admin_id else ""}status = 5',
                      where=f'id = {order_id}')
        cancel_text += f' администратором' if admin_id else ''
        if discount:
            cancel_text += f", вам возвращено {discount} бонусов на баланс."
            users.update(f'bonus = bonus + {discount}', where=f'id = {user_id}')
        return cancel_text
    orders.update(f'date_end = "{date}", status = 5', where=f'id = {order_id}')
    cancel_text += f'. Поскольку вы не дождались получения заказа, ' \
                   f'потраченные бонусы в размере {discount} руб. на баланс не вернутся.' if discount else '.'
    return cancel_text


async def get_order_info(order_id, is_admin=False) -> str:
    """Возвращает полную информацию о заказе в архиве"""
    order = orders.print_table('user_id', 'date_start', 'date_order', 'date_accept', 'date_end', 'body', 'price',
                               'bonus', 'status', 'comment', where=f'id = {order_id}')
    user_id, date_start, date_order, date_accept, date_end, body, price, discount, status, comment = order[0]
    body_text = await get_order_list_text(await get_basket(user_id, body))
    name_status = types_base.print_table('name', where=f'base = "orders" and typ = {status}')[0][0]
    if not status:
        if not price:
            price = "будет рассчитана после совершения заказа или в момент списания бонусов."
    txt = f"Информация о заказе № {order_id}:\nID пользователя: {user_id}\n\n"
    txt += f"Дата создания корзины:\n{date_start}\nДата отправки заказа в обработку:\n{date_order}\n" \
           f"Дата принятия заказа:\n{date_accept}\nДата завершения заказа:\n{date_end}\n" if not is_admin else ""
    txt += f'Состав заказа:\n{body_text}\n\nСтоимость{" (с учетом скидки)" if discount else ""}: {price} руб.\n' \
           f'Скидка: {discount} руб.\nСтатус заказа: {name_status}\nКомментарий:\n{comment}\n'
    return txt


async def get_order_status(order_id) -> int:
    """Возвращает текущий статус заказа """
    return orders.print_table('status', where=f'id = {order_id}')[0][0]


def decor_check_username(func):
    """Проверка, был ли изменен username в Telegram"""
    async def wrapper(message: types.Message | types.CallbackQuery):
        tg_id = await get_tg_id(message)
        username = users.print_table('username', where=f'tg_id = {tg_id}')[0][0]
        if message["from"].username != username:
            await add_log(f"TG_{tg_id} username изменен с [{username}] на [{message['from'].username}]")
            users.update(f'username = "{message["from"].username}"', where=f'tg_id = {tg_id}')
        return await func(message)
    return wrapper


async def remake_order(order_id, user_id) -> None:
    """Функция для кнопки "Повторить заказ" в архиве заказов."""
    body = orders.print_table('body', where=f'id = {order_id}')[0][0]
    await check_order(user_id, is_user_id=True)
    orders.update(f'body = "{body}"', where=f'user_id = {user_id} and status = 0')
