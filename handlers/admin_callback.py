from aiogram import types, Dispatcher
from config import bot
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageNotModified
from functions import get_tg_id, add_log, status_changer, get_order_info, admin_order_work, send_to_admins
from functions import get_food_text, inline_private, get_text_message, make_message_read
from keyboards import kb_client_inline_menu, kb_admin_order_inline_button, kb_client_inline_order_cancel_button
from keyboards import kb_admin_edit_cafe_inline_menu, kb_admin_answer_message_inline_button


# =======================================
#                CAFE MENU
# =======================================
@inline_private
async def client_inline_menu_admin(callback: types.CallbackQuery):
    """Функция-хэндлер клавиатуры kb_client_inline_menu, кнопки администратора"""
    tg_id = await get_tg_id(callback)
    cmd, *data = callback.data.split("_")[1:]
    is_new_message = False
    match cmd:

        case "change":
            food_id, type_food = data
            res = await status_changer(food_id)
            res = 'в наличии' if res else 'нет в наличии'
            text, cb_text = f"TG_{tg_id} сменил доступность блюда ID_{food_id} на [{res}]", f"Изменено на [{res}]"
            kb = await kb_client_inline_menu(type_food, tg_id, current_id=int(food_id))

        case "edit":
            food_id, type_food = data
            text, cb_text = f"TG_{tg_id} хочет отредактировать блюдо ID_{food_id}", f"Редактировать блюдо."
            text_new_message, image = await get_food_text(food_id)
            text_new_message += "\n\n<b>Выберите то, что необходимо редактировать:</b>"
            kb, is_new_message = await kb_admin_edit_cafe_inline_menu(food_id), True

    await add_log(text)
    try:
        await bot.send_photo(tg_id, photo=image, caption=text_new_message, reply_markup=kb, parse_mode='html') \
            if is_new_message else await callback.message.edit_reply_markup(reply_markup=kb)
    except MessageNotModified:
        pass
    return await callback.answer(cb_text)

# =======================================
#              END CAFE MENU
# =======================================


# =======================================
#                ORDERS
# =======================================
@inline_private
async def admin_order_inline_handler(callback: types.CallbackQuery):
    """Функция предназначенная администраторам для работы с заказами пользователей"""
    tg_id = await get_tg_id(callback)
    cmd, order_id = callback.data.split("_")[1:]
    is_new_message = False
    match cmd:

        case "accept" | "complete" | "cancel" | "successfully" | "unsuccessfully":
            text, cb_text = f"TG_{tg_id} нажал на кнопку {cmd} в заказе ID_{order_id}", "Успешно!"
            res = await admin_order_work(tg_id, order_id, cmd)
            if type(res) == str:
                return await callback.answer(res, show_alert=True)
            text_to_admins, text_for_user, user_tg = res
            await send_to_admins(text_to_admins)
            await bot.send_message(user_tg, text_for_user,
                                   reply_markup=await kb_client_inline_order_cancel_button(order_id))
            kb = await kb_admin_order_inline_button(order_id)
            new_text_message = await get_order_info(order_id, is_admin=True)

        case "show":
            text, cb_text = f"TG_{tg_id} просматривает информацию о заказе ID_{order_id}", "Открываю заказ"
            kb, is_new_message = await kb_admin_order_inline_button(order_id), True
            text_new_message = await get_order_info(order_id, is_admin=True)

    await add_log(text)
    await callback.message.edit_text(text=new_text_message, reply_markup=kb) if not is_new_message else \
        await bot.send_message(tg_id, text_new_message, reply_markup=kb)
    return await callback.answer(cb_text)

# =======================================
#              END ORDERS
# =======================================


# =======================================
#                MESSAGES
# =======================================
@inline_private
async def admin_current_messages_inline_menu(callback: types.CallbackQuery):
    """Функция предназначенная администраторам для работы с сообщениями от пользователей"""
    tg_id = await get_tg_id(callback)
    cmd, message_id = callback.data.split("_")[1:]
    is_new_message = False
    match cmd:

        case "read":
            text, cb_text = f"TG_{tg_id} отметил прочтённым сообщение ID_{message_id}", "Прочитано!"
            res = await make_message_read(tg_id, message_id)
            if res:
                return await callback.answer(res, show_alert=True)
            await send_to_admins(f"Администратор {text}\n\n{await get_text_message(message_id)}")
            kb = await kb_admin_answer_message_inline_button(message_id)

        case "open":
            text, cb_text = f"TG_{tg_id} просматривает сообщение ID_{message_id}", "Открываю сообщение"
            is_new_message, text_new_message = True, await get_text_message(message_id)
            kb = await kb_admin_answer_message_inline_button(message_id)

    await add_log(text)
    await callback.message.edit_reply_markup(reply_markup=kb) if not is_new_message else \
        await bot.send_message(tg_id, text_new_message, reply_markup=kb)
    return await callback.answer(cb_text)

# =======================================
#              END MESSAGES
# =======================================


# ====================== LOADING ======================
def register_inline_handlers_admin(dp: Dispatcher):
    """Регистрация хэндлеров"""
    dp.register_callback_query_handler(client_inline_menu_admin, Text(startswith="cma_"))
    dp.register_callback_query_handler(admin_order_inline_handler, Text(startswith="koa_"))
    dp.register_callback_query_handler(admin_current_messages_inline_menu, Text(startswith="kama_"))
