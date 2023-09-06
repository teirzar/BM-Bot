from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from functions import add_log, get_tg_id, get_user_id
from config import bot
from keyboards import kb_client_inline_menu, kb_client_inline_menu_info, kb_client_basket


async def client_inline_menu(callback: types.CallbackQuery):
    """Функция-хэндлер клавиатуры kb_client_inline_menu"""
    user_id, tg_id = await get_user_id(callback), await get_tg_id(callback)
    cmd, point, type_food, point2 = callback.data.split("_")[1:]
    match cmd:
        case "current":
            if point == point2:
                return await callback.answer("Данное блюдо уже выбрано. "
                                             "Вы можете посмотреть информацию; добавить или отнять количество позиций; "
                                             "а также удалить товар из корзины.", show_alert=True)
            text = f"ID_{user_id} выбрал блюдо ID_{point}"
            kb = await kb_client_inline_menu(type_food, tg_id, current_id=int(point))
    await add_log(text)
    return await callback.message.edit_reply_markup(reply_markup=kb)


# ====================== LOADING ======================
def register_inline_handlers_client(dp: Dispatcher):
    """Регистрация хэндлеров"""
    dp.register_callback_query_handler(client_inline_menu, Text(startswith="cm_"))
