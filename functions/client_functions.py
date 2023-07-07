from aiogram import types
from config import users, bonus


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
    if users_dict['status'] != 3:
        need_money = total_prices[users_dict['status'] + 1] - users_dict['total_price']
    next_status = "\n<i>До статуса '" + status[users_dict['status']+1] + f"': {need_money}р.</i>" if need_money else ''
    text = f"""<b>Ваш профиль</b>\n
    🆔 ID: {users_dict['id']}
    📇 Имя: {users_dict['name']}
    📱 Телефон: {users_dict['phone'] if users_dict['phone'] else "Укажите телефон в настройках!"}
    💰 Бонусы: {users_dict['bonus']}
    😎 Статус: {status[users_dict['status']]}{next_status}
    🔔 Уведомления: {"вкл." if users_dict['notification'] else "выкл."}
    \nИзменить данные можно в\n⚙ Настройках (/settings)"""
    return text


# get prev orders text
async def get_prev_orders(user_id) -> str:
    """Возвращает текст о последних заказах пользователя, если его нет, возвращает текст о том, что список пуст.
    Необходимо для функции 'Мои заказы' """
    return "Ваши заказы: В РАЗРАБОТКЕ"
