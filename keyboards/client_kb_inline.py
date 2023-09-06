from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from functions import get_admins, get_food_kb_info
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
    for i, n, w, p, s in lst:
        if s or is_admin:
            text = f"{n} ({w}{pt}), {p} руб."
            if is_admin:
                text = f'{n + (" ✅" if s else " ❌")}, {p} р.'
            ikb.add(InlineKeyboardButton(text, callback_data=f'cm_current_{i}_{type_food}_{current_id}'))

        if current_id == i:
            if is_admin:
                ikb.row(InlineKeyboardButton("ℹ", callback_data=f'cm_info_{i}__'),
                        InlineKeyboardButton(" ❌" if s else " ✅", callback_data='s'),
                        InlineKeyboardButton("✏", callback_data='edit')
                        )
            else:
                ikb.row(InlineKeyboardButton("ℹ", callback_data=f'cm_info_{i}__'),
                        InlineKeyboardButton("➖", callback_data='s'),
                        InlineKeyboardButton("0", callback_data='edit'),
                        InlineKeyboardButton("➕", callback_data='i'),
                        InlineKeyboardButton(" ❌", callback_data='s')
                        )
    if not is_admin:
        ikb.row(InlineKeyboardButton("💵 Заказ", callback_data='i'),
                InlineKeyboardButton("🛒 0", callback_data='s'),
                InlineKeyboardButton("🗑 Очистить", callback_data='edit')
                )
    return ikb


async def kb_client_inline_menu_info(food_id, user_id):
    """Карточка товара, подробная информация о товаре"""
    typ, dislike, like, basket, count = await get_food_kb_info(food_id, user_id)
    ikb = InlineKeyboardMarkup()
    b1 = InlineKeyboardButton(f"👎 {dislike}", callback_data=f"dislike")
    b2 = InlineKeyboardButton("➖", callback_data=f"minus")
    b3 = InlineKeyboardButton(f"🛒 {count}", callback_data=f"basket")
    b4 = InlineKeyboardButton("➕", callback_data=f"plus")
    b5 = InlineKeyboardButton(f"👍 {like}", callback_data=f"like")
    ikb.row(b1, b2, b3, b4, b5)
    if basket:
        b6 = InlineKeyboardButton(f"➕🍟", callback_data="snack")
        b7 = InlineKeyboardButton(f"$ {basket}р.", callback_data=f"buying_start")
        b8 = InlineKeyboardButton(f"➕🥤 ", callback_data="drink")
        if int(typ) not in (40, 50, 60):
            ikb.add(b6, b7, b8)
        elif int(typ) == 40:
            return ikb.add(b8, b7, btclose)
        else:
            return ikb.add(b6, b7, btclose)
    ikb.add(btclose)
    return ikb


# =======================================
#              END CAFE MENU
# =======================================


# =======================================
#                 BASKET
# =======================================


async def kb_client_basket(basket):
    """Клавиатура корзины"""
    ikb = InlineKeyboardMarkup()
    for i, count in basket.items():
        b1 = InlineKeyboardButton(cafe.print_table('name', where=f'id = {i}')[0][0], callback_data=f'plus')
        b2 = InlineKeyboardButton("i", callback_data=f"info")
        b3 = InlineKeyboardButton("-", callback_data=f"minus")
        b4 = InlineKeyboardButton(f"{count} шт.", callback_data=f"u_vas_v_korzine_{count}_sht")
        b5 = InlineKeyboardButton("+", callback_data=f"plus")
        b6 = InlineKeyboardButton("x", callback_data=f"delete")
        ikb.add(b1).row(b2, b3, b4, b5, b6)
    ikb.add(InlineKeyboardButton("💵 К оформлению.", callback_data='buying_start'))
    return ikb


# =======================================
#               END BASKET
# =======================================
