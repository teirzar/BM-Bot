from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from functions import add_log, get_tg_id, get_user_id, get_food_text, set_order
from aiogram.utils.exceptions import MessageCantBeDeleted, BadRequest, MessageNotModified
from config import bot
from keyboards import kb_client_inline_menu, kb_client_inline_menu_info, kb_client_basket


async def cmd_close_inline_handler(callback: types.CallbackQuery):
    """Функция закрытия клавиатуры"""
    try:
        await callback.message.delete()
    except MessageCantBeDeleted:
        try:
            return await callback.message.edit_text("Удалено")
        except BadRequest:
            return await callback.answer("Слишком старое сообщение, невозможно его удалить\n"
                                         "Удалите сообщение у себя в диалоге", show_alert=True)
    return await callback.answer("Закрыл")


async def client_inline_menu(callback: types.CallbackQuery):
    """Функция-хэндлер клавиатуры kb_client_inline_menu"""
    user_id, tg_id = await get_user_id(callback), await get_tg_id(callback)
    cmd, *data = callback.data.split("_")[1:]
    new_message = False
    match cmd:

        case "current":
            food_id, type_food, current_id = data
            if food_id == current_id:
                return await callback.answer("Данное блюдо уже выбрано. "
                                             "Вы можете посмотреть информацию; добавить или отнять количество позиций; "
                                             "а также удалить товар из корзины.", show_alert=True)
            text = f"ID_{user_id} выбрал блюдо ID_{food_id}"
            kb = await kb_client_inline_menu(type_food, tg_id, current_id=int(food_id))

        case "info":
            food_id = data[0]
            text = f"ID_{user_id} открыл инфо о блюде ID_{food_id}"
            text_new_message, image = await get_food_text(food_id)
            kb, new_message = await kb_client_inline_menu_info(food_id, user_id), True

        case "show":
            return await callback.answer("")

        case "food":
            food_id, cmd, type_food = data
            res = await set_order(user_id, food_id, cmd)
            if type(res) is str:
                return await callback.answer(res, show_alert=True)
            kb = await kb_client_inline_menu(type_food, tg_id, current_id=int(food_id))
            text = f"ID_{user_id} выбрал <{cmd}> блюдо ID_{food_id}"

    await add_log(text)
    return await bot.send_photo(tg_id, photo=image, caption=text_new_message, reply_markup=kb, parse_mode='html') if \
        new_message else await callback.message.edit_reply_markup(reply_markup=kb)


# ====================== LOADING ======================
def register_inline_handlers_client(dp: Dispatcher):
    """Регистрация хэндлеров"""
    dp.register_callback_query_handler(cmd_close_inline_handler, Text(equals="close_inline_handler"))
    dp.register_callback_query_handler(client_inline_menu, Text(startswith="cm_"))

