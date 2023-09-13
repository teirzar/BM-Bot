from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from functions import get_admins, get_food_kb_info, get_count, get_basket, get_orders, get_order_status
from config import cafe, orders

# Кнопка закрыть клавиатуру
btclose = InlineKeyboardButton("[X] Закрыть", callback_data=f"close_inline_handler")


# =======================================
#                CAFE MENU
# =======================================

async def kb_client_inline_menu(type_food, tg_id, current_id=None):
    """Список позиций заведения по выбранной категории товаров"""
    ikb = InlineKeyboardMarkup(row_width=3)
    lst = cafe.print_table('id', 'name', 'weight', 'price', 'status', where=f'type = {type_food}')
    pt = "гр" if type_food not in (50, 60) else "мл"
    is_admin = tg_id in await get_admins()
    basket_count, total_price, food_count = await get_count(tg_id, current_id)
    for i, n, w, p, s in lst:
        if s or is_admin:
            text = f"{n} ({w}{pt}), {p} руб."
            if is_admin:
                text = f'{n + (" ✅" if s else " ❌")}, {p} р.'
            ikb.add(InlineKeyboardButton(text, callback_data=f'cm_current_{i}_{type_food}_{current_id}'))

        if current_id == i:
            if is_admin:
                ikb.row(InlineKeyboardButton("ℹ", callback_data=f'cm_info_{i}'),
                        InlineKeyboardButton(" ❌" if s else " ✅", callback_data=f'cma_change_{i}_{type_food}'),
                        InlineKeyboardButton("✏", callback_data=f'cma_edit_{i}_{type_food}'),
                        )
            else:
                ikb.row(InlineKeyboardButton("ℹ", callback_data=f'cm_info_{i}'),
                        InlineKeyboardButton("➖", callback_data=f'cm_food_{i}_minus_{type_food}'),
                        InlineKeyboardButton(f"{food_count}", callback_data=f'bs_show_'),
                        InlineKeyboardButton("➕", callback_data=f'cm_food_{i}_plus_{type_food}'),
                        InlineKeyboardButton(" ❌", callback_data=f'cm_food_{i}_delete_{type_food}'),
                        )
    if not is_admin:
        ikb.row(InlineKeyboardButton("💵 Заказ", callback_data='bs_order_'),
                InlineKeyboardButton(f"{basket_count}🛒, {total_price}р", callback_data='bs_open_'),
                InlineKeyboardButton("🗑 Очистить", callback_data=f'bs_clear_{type_food}'),
                )
    ikb.add(btclose)
    return ikb


async def kb_client_inline_menu_info(food_id, tg_id):
    """Карточка товара, подробная информация о товаре"""
    typ, dislike, like = await get_food_kb_info(food_id)
    basket_count, total_price, food_count = await get_count(tg_id, food_id)
    is_admin = tg_id in await get_admins()
    ikb = InlineKeyboardMarkup()
    if not is_admin:
        b1 = InlineKeyboardButton(f"👎 {dislike}", callback_data=f"cmi_dislike_{food_id}")
        b2 = InlineKeyboardButton("➖", callback_data=f"cmi_minus_{food_id}")
        b3 = InlineKeyboardButton(f"{food_count}", callback_data=f"bs_show_")
        b4 = InlineKeyboardButton("➕", callback_data=f"cmi_plus_{food_id}")
        b5 = InlineKeyboardButton(f"👍 {like}", callback_data=f"cmi_like_{food_id}")
        ikb.row(b1, b2, b3, b4, b5)
    if food_count and not is_admin:
        b6 = InlineKeyboardButton(f"➕🍟", callback_data="cmi_open_snack")
        b7 = InlineKeyboardButton(f"🛒 {total_price}р", callback_data=f"bs_open_")
        b8 = InlineKeyboardButton(f"➕🥤 ", callback_data="cmi_open_drink")
        if int(typ) not in (40, 50, 60):
            ikb.add(b6, b7, b8)
        elif int(typ) == 40:
            ikb.add(b8, b7)
        else:
            ikb.add(b6, b7)
    ikb.add(btclose)
    return ikb

# =======================================
#              END CAFE MENU
# =======================================


# =======================================
#                 BASKET
# =======================================

async def kb_client_inline_basket_menu(user_id):
    """Клавиатура корзины"""
    ikb = InlineKeyboardMarkup()
    basket = await get_basket(user_id)
    for i, count in basket.items():
        name, price = cafe.print_table('name', 'price', where=f'id = {i}')[0]
        b1 = InlineKeyboardButton(f'{name} {price}р. (x{count} = {price*count}р.)', callback_data=f'cb_info_{i}')
        b2 = InlineKeyboardButton("ℹ", callback_data=f"cb_info_{i}")
        b3 = InlineKeyboardButton("➖", callback_data=f"cb_food_{i}_minus")
        b4 = InlineKeyboardButton(f"{count} шт.", callback_data=f"bs_show_")
        b5 = InlineKeyboardButton("➕", callback_data=f"cb_food_{i}_plus")
        b6 = InlineKeyboardButton(" ❌", callback_data=f"cb_food_{i}_delete")
        ikb.add(b1).row(b2, b3, b4, b5, b6)
    if basket:
        ikb.add(InlineKeyboardButton("💵 К оформлению.", callback_data='bs_order_'),
                InlineKeyboardButton("🗑 Очистить", callback_data='bs_clear_'))
    ikb.add(btclose)
    return ikb


# =======================================
#               END BASKET
# =======================================


# =======================================
#                 ORDER
# =======================================

async def kb_client_inline_order_menu(user_id, bonus, current_discount):
    """Клавиатура подтверждения и оформления заказа"""
    ikb = InlineKeyboardMarkup()
    basket = await get_basket(user_id)
    if not basket:
        return ikb.add(btclose)
    if bonus > 0 and not current_discount:
        b1 = InlineKeyboardButton("Списать бонусы", callback_data=f"om_bonus")
        ikb.add(b1)
    b2 = InlineKeyboardButton("Комментарий", callback_data=f"write_comment")
    b3 = InlineKeyboardButton("Все верно", callback_data=f"om_buy")
    ikb.add(b2, b3).add(btclose)
    return ikb


async def kb_client_inline_prev_orders_menu(user_id):
    """Клавиатура для меню архива заказов"""
    ikb = InlineKeyboardMarkup()
    order_list = str(await get_orders(user_id))
    types = ["🛒", "🔄", "🕓", "🍴", "✅", "❌"]
    if order_list:
        lst = {k: v for k, *v in orders.print_table('id', 'date_start', 'date_order', 'price', 'status',
                                                    where=f'user_id = {user_id}')}
        for order_id in order_list.split()[:-21:-1]:
            order_id = int(order_id)
            date_1, date_2, price, status = lst[order_id][0], lst[order_id][1], lst[order_id][2], lst[order_id][-1]
            ikb.add(InlineKeyboardButton(f"№{order_id}: {date_2 if date_2 else date_1}, {price} руб. {types[status]}",
                                         callback_data=f"order_{order_id}"))
    return ikb.add(btclose)


async def kb_client_inline_order_cancel_button(order_id, is_return=False):
    """Кнопка отмены заказа"""
    ikb = InlineKeyboardMarkup()
    status = await get_order_status(order_id)
    b1 = InlineKeyboardButton(f"Отменить заказ №{order_id} ❌", callback_data=f"oc_cancel_{order_id}")
    if status in (1, 2):
        ikb.add(b1)
    if is_return:
        b2 = InlineKeyboardButton(f"Повторить заказ №{order_id} 🔁", callback_data=f"oc_reorder_{order_id}")
        b3 = InlineKeyboardButton(f"Сделать заказ №{order_id} 💵", callback_data=f"bs_order_")
        ikb.add(b2 if status else b3)
        return ikb.add(InlineKeyboardButton("Назад", callback_data="bs_return_"), btclose)
    return ikb.add(btclose)

# =======================================
#               END ORDER
# =======================================
