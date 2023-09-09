from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from functions import get_order_status, get_current_orders_admin
from keyboards import btclose


# =======================================
#                ORDERS
# =======================================
async def kb_admin_order_inline_button(order_id):
    """Клавиши администратора, прикрепляемые к окну с заказом"""
    status = await get_order_status(order_id)
    is_accepted = is_complete = False
    if status == 2:
        is_accepted = True
    if status == 3:
        is_complete = True
    ikb = InlineKeyboardMarkup()
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
    ikb = InlineKeyboardMarkup()
    current_orders = await get_current_orders_admin()
    types = ["🛒", "🔄", "🕓", "🍴", "✅", "❌"]
    for i, u, p, s in current_orders:
        ikb.add(InlineKeyboardButton(f'№{i} от ID{u} на {p} руб. {types[s]}', callback_data=f'koa_show_{i}'))
    return ikb.add(btclose)

# =======================================
#              END ORDERS
# =======================================
