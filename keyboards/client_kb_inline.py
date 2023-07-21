from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from functions import get_admins
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
            ikb.add(InlineKeyboardButton(text, callback_data=f'{i}'))

        if current_id == i:
            if is_admin:
                ikb.row(InlineKeyboardButton("ℹ", callback_data='i'),
                        InlineKeyboardButton(" ❌" if s else " ✅", callback_data='s'),
                        InlineKeyboardButton("✏", callback_data='edit')
                        )
            else:
                ikb.row(InlineKeyboardButton("ℹ", callback_data='i'),
                        InlineKeyboardButton("➖", callback_data='s'),
                        InlineKeyboardButton("0", callback_data='edit'),
                        InlineKeyboardButton("➕", callback_data='i'),
                        InlineKeyboardButton(" ❌", callback_data='s')
                        )
    if not is_admin:
        ikb.row(InlineKeyboardButton("🛒 В корзину", callback_data='i'),
                InlineKeyboardButton("0", callback_data='s'),
                InlineKeyboardButton("🗑 Очистить", callback_data='edit')
                )
    return ikb

# =======================================
#              END CAFE MENU
# =======================================
