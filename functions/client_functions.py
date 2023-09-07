from aiogram import types
from config import users, bonus, types_base, cafe, orders
from functions import get_time


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


# get profile text
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


# get prev orders text
async def get_prev_orders(user_id) -> str:
    """Возвращает текст о последних заказах пользователя, если его нет, возвращает текст о том, что список пуст.
    Необходимо для функции 'Мои заказы' """
    return "Ваши заказы: В РАЗРАБОТКЕ"


async def get_type_food_id(text) -> int:
    """Функция возвращает ID типа товарной позиции,
    для дальнейшего вызова соответствующего инлайна по запросу пользователя"""
    food_type = types_base.print_table('typ', where=f'base = "cafe" and name = "{text[1:].strip()}"')
    return food_type[0][0]


async def get_food_kb_info(food_id) -> tuple:
    """"Возвращает кортеж данных, необходимых для функционирования клавиатуры карточки товара.
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
    if not lst:
        lst = orders.print_table('body', where=f'user_id = {user_id} and status = 0')[0][0]
    basket = {el.split(":")[0]:int(el.split(":")[1]) for el in lst.split()}
    return basket


async def set_order(user_id, food_id, cmd) -> str | int:
    """Функция для изменения состояния заказа в корзине, выбор действия с товаром и реализация действия"""
    order_id, current_lst = orders.print_table('id', 'body', where=f'user_id = {user_id} and status = 0')[0]
    current_basket = await get_basket(user_id, current_lst) if current_lst else {}

    match cmd:
        case "plus":
            if food_id not in current_basket:
                if len(current_basket) > 11:
                    return "Нельзя одновременно добавить более 12 различных товаров!"
                new_food = current_lst + f" {food_id}:1"
                orders.update(f'body = "{new_food}"', where=f'id = {order_id}')
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

    orders.update(f'body = "{" ".join([f"{f}:{c}" for f, c in current_basket.items()])}"', where=f'id = {order_id}')
    return current_basket.get(food_id, 0)


async def get_count(tg_id, current_id=None) -> tuple:
    """Функция для того, чтобы узнать какое количество конкретных позиций у пользователя в заказе,
    а так же стоимость и количество ВСЕХ товаров в корзине"""
    user_id = users.print_table('id', where=f'tg_id = {tg_id}')[0][0]

    if (user_id, ) not in orders.print_table('user_id'):
        orders.write('user_id', 'body', 'date_start', 'status', values=f'{user_id}, "", "{await get_time()}", 0')

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


async def get_text_basket(tg_id, user_id) -> str:
    """Функция для генерации и возврата строки с информацией о заполненности корзины пользователя"""
    basket = await get_basket(user_id)
    basket_count, total_price, food_count = await get_count(tg_id)
    text = f"В вашей корзине\n{basket_count} товара(-ов) на сумму {total_price} руб:\n\n" \
        if len(basket) else "Ваша корзина пуста."

    return text
