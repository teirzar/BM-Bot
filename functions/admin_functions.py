from functions import get_order_list_text, get_basket


async def get_order_text(user_id, res):
    """Функция генерирует текст для админа о содержании заказа пользователя,
    res - tuple, в котором 3 переменные:
    price заказа, discount - скидка, lst - список товаров пользователя, order_id - id заказа в базе"""
    price, discount, lst, order_id = res
    text = f"Новый заказ ID_{order_id} от пользователя ID_{user_id}!\nСписок позиций:\n\n"
    text += await get_order_list_text(await get_basket(user_id, lst=lst))
    text += f"\nСумма заказа: {price}\nСкидка составила: {discount}"
    return text
