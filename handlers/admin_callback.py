from aiogram import types, Dispatcher
from config import bot
from aiogram.dispatcher.filters import Text
from functions import get_tg_id, add_log, status_changer, get_order_info, admin_order_work
from keyboards import kb_client_inline_menu, kb_admin_order_inline_button


# =======================================
#                CAFE MENU
# =======================================
async def client_inline_menu_admin(callback: types.CallbackQuery):
    """Функция-хэндлер клавиатуры kb_client_inline_menu, кнопки администратора"""
    tg_id = await get_tg_id(callback)
    cmd, *data = callback.data.split("_")[1:]
    match cmd:
        case "change":
            food_id, type_food = data
            res = await status_changer(food_id)
            res = 'в наличии' if res else 'нет в наличии'
            text, cb_text = f"TG_{tg_id} сменил доступность блюда ID_{food_id} на [{res}]", f"Изменено на [{res}]"
            kb = await kb_client_inline_menu(type_food, tg_id, current_id=int(food_id))

        case "edit":
            ...

    await add_log(text)
    await callback.message.edit_reply_markup(reply_markup=kb)
    return await callback.answer(cb_text)


# =======================================
#              END CAFE MENU
# =======================================


# =======================================
#                ORDERS
# =======================================
async def admin_order_inline_handler(callback: types.CallbackQuery):
    """Функция предназначенная администраторам для работы с заказами пользователей"""
    tg_id = await get_tg_id(callback)
    cmd, order_id = callback.data.split("_")[1:]
    is_new_message = False

    match cmd:
        case "accept" | "complete" | "cancel" | "successfully" | "unsuccessfully":
            text, cb_text = f"TG_{tg_id} нажал на кнопку {cmd} в заказе ID_{order_id}", "Успешно!"
            text_for_user, text_for_admins = await admin_order_work(order_id, tg_id)
            ...
        case "show":
            text, cb_text = f"TG_{tg_id} просматривает информацию о заказе ID_{order_id}", "Открываю заказ."
            kb, is_new_message = await kb_admin_order_inline_button(order_id), True
            text_new_message = await get_order_info(order_id, is_admin=True)

    await add_log(text)
    await callback.message.edit_reply_markup(reply_markup=kb) if not is_new_message else \
        await bot.send_message(tg_id, text_new_message, reply_markup=kb)
    return await callback.answer(cb_text)
# =======================================
#              END ORDERS
# =======================================

# ====================== LOADING ======================
def register_inline_handlers_admin(dp: Dispatcher):
    """Регистрация хэндлеров"""
    dp.register_callback_query_handler(client_inline_menu_admin, Text(startswith="cma_"))
    dp.register_callback_query_handler(admin_order_inline_handler, Text(startswith="koa_"))
