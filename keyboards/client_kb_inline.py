from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from functions import get_admins, get_food_kb_info, get_count, get_basket
from config import cafe


# Кнопка закрыть клавиатуру
btclose = InlineKeyboardButton("[X] Закрыть", callback_data=f"close_inline_handler")


# =======================================
#                CAFE MENU
# =======================================

async def kb_client_inline_menu(type_food, tg_id, current_id=None):
    """Список позиций заведения по выбранной категории товаров"""
    ikb = InlineKeyboardMarkup(row_width=3)
    lst = cafe.print_table('id', 'name', 'weight', 'price', 'status', where=f'type = {type_food}')
    pt = "гр" if type_food != 50 else "мл"
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
                        InlineKeyboardButton(" ❌" if s else " ✅", callback_data='s'),
                        InlineKeyboardButton("✏", callback_data='edit')
                        )
            else:
                ikb.row(InlineKeyboardButton("ℹ", callback_data=f'cm_info_{i}'),
                        InlineKeyboardButton("➖", callback_data=f'cm_food_{i}_minus_{type_food}'),
                        InlineKeyboardButton(f"{food_count}", callback_data=f'bs_show_'),
                        InlineKeyboardButton("➕", callback_data=f'cm_food_{i}_plus_{type_food}'),
                        InlineKeyboardButton(" ❌", callback_data=f'cm_food_{i}_delete_{type_food}')
                        )
    if not is_admin:
        ikb.row(InlineKeyboardButton("💵 Заказ", callback_data='bs_order_'),
                InlineKeyboardButton(f"{basket_count}🛒, {total_price}р", callback_data='bs_open_'),
                InlineKeyboardButton("🗑 Очистить", callback_data=f'bs_clear_{type_food}')
                )
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
        b7 = InlineKeyboardButton(f"{basket_count}🛒, {total_price}р", callback_data=f"bs_open_")
        b8 = InlineKeyboardButton(f"➕🥤 ", callback_data="cmi_open_drink")
        if int(typ) not in (40, 50, 60):
            ikb.add(b7).add(b6, b8)
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


async def kb_client_inline_basket(user_id):
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
