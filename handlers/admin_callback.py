from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from functions import get_user_id, get_tg_id, add_log, status_changer
from keyboards import kb_client_inline_menu


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


# ====================== LOADING ======================
def register_inline_handlers_admin(dp: Dispatcher):
    """Регистрация хэндлеров"""
    dp.register_callback_query_handler(client_inline_menu_admin, Text(startswith="cma_"))
