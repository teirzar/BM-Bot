from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from functions import get_order_status, get_current_orders_admin, get_cafe_column_names
from keyboards import btclose


# =======================================
#                ORDERS
# =======================================
async def kb_admin_order_inline_button(order_id):
    """Клавиши администратора, прикрепляемые к окну с заказом"""
    status = await get_order_status(order_id)
    ikb = InlineKeyboardMarkup()
    if status in (4, 5):
        return ikb.add(btclose)
    is_accepted = is_complete = False
    if status == 2:
        is_accepted = True
    if status == 3:
        is_complete = True
    b1 = InlineKeyboardButton("Принять", callback_data=f'koa_accept_{order_id}')
    b2 = InlineKeyboardButton("Заказ готов!", callback_data=f'koa_complete_{order_id}')
    b3 = InlineKeyboardButton("Отменить", callback_data=f'koa_cancel_{order_id}')
    b4 = InlineKeyboardButton("Заказ забрали", callback_data=f'koa_successfully_{order_id}')
    b5 = InlineKeyboardButton("Заказ не забрали", callback_data=f'koa_unsuccessfully_{order_id}')
    if is_complete:
        ikb.add(b4, b5)
    else:
        ikb.add(b2 if is_accepted else b1, b3)
    return ikb.add(btclose)


async def kb_admin_current_orders_inline_menu():
    """Клавиатура, предназначенная для вывода в сообщение активных заказов"""
    ikb = InlineKeyboardMarkup()
    current_orders = await get_current_orders_admin()
    types = ["🛒", "🔄", "🕓", "🍴", "✅", "❌"]
    for i, u, p, s in current_orders:
        ikb.add(InlineKeyboardButton(f'№{i} от ID{u} на {p} руб. {types[s]}', callback_data=f'koa_show_{i}'))
    return ikb.add(btclose)

# =======================================
#              END ORDERS
# =======================================


# =======================================
#                  CAFE
# =======================================
async def kb_admin_edit_cafe_inline_menu(food_id):
    """Клавиатура для выбора колонки для редактирования блюда"""
    ikb = InlineKeyboardMarkup(row_width=2)
    for column, name in (await get_cafe_column_names()).items():
        ikb.insert(InlineKeyboardButton(name, callback_data=f"kea_edit_{column}_{food_id}"))
    return ikb.add(btclose)

# =======================================
#                END CAFE
# =======================================
