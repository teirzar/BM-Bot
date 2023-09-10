from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram import types, Dispatcher
from aiogram.utils.exceptions import BotBlocked
from config import bot, messages, users, cafe
from functions import get_tg_id, add_log, get_current_food_value, get_admins, get_user_id
from keyboards import kb_cancel_button, kb_client_main_menu, kb_client_cafe_menu


# ========================================================
#                        CANCEL
# ========================================================

async def cancel_button(message: types.Message, state: FSMContext):
    """Функция отмены машины состояний"""
    tg_id = message['from'].id
    user_id = await get_user_id(message)
    current_state = await state.get_state()
    if current_state is None:
        return
    await add_log(f"ID_{user_id}: [Отмена {current_state}]")
    await bot.send_message(tg_id, f"Отменено.", reply_markup=await kb_client_main_menu())
    return await state.finish()

# ========================================================
#                       END CANCEL
# ========================================================


# ========================================================
#                       EDIT FOOD
# ========================================================
class AdminEditFood(StatesGroup):
    """Редактирование блюда в базе данных"""
    value = State()
    column = None
    food_id = None
    current_value = None


async def admin_edit_food(callback: types.CallbackQuery):
    column, food_id = callback.data.split('_')[1:]
    AdminEditFood.food_id, AdminEditFood.column = food_id, column
    tg_id = await get_tg_id(callback)
    await AdminEditFood.value.set()
    await add_log(f"TG_{tg_id} открыл форму редактирования блюда ID_{food_id}, колонка: {column}.")
    AdminEditFood.current_value = str(await get_current_food_value(food_id, column))
    text = "Текущее значение:\n" + AdminEditFood.current_value
    text += "\n"
    match column:
        case "name":
            text += "(Вводите корректное значение наименования позиции)\n"
        case "price" | "weight":
            text += "(Допускаются к написанию исключительно положительные числовые значения!)\n"
        case "caption":
            text += "(Введите желаемое описание блюда)\n"
        case "image":
            text += "(Отправьте ссылку на картинку, которую необходимо закрепить с товарной позицией!)\n"
        case "composition":
            text += "(Вводите состав блюда, включая соусы (если они есть).)\n"
    text += "\nНапишите 'Отмена' чтобы выйти!\n\nВведите новое значение:\n"
    await callback.answer(f"Редактирование значения колонки {column}")
    await callback.message.answer(text, reply_markup=await kb_cancel_button())


async def admin_edit_food_reply(message: types.Message, state: FSMContext):
    tg_id = await get_tg_id(message)
    async with state.proxy() as data:
        data["value"] = message.text.replace('"', "''")
    value = data['value']
    match AdminEditFood.column:
        case "name" | "caption" | "image" | "composition":
            if AdminEditFood.column == 'image' and "://" not in value:
                return await message.answer("Неверно указана ссылка, введите еще раз")
            value = f'"{value}"'
        case "price" | "weight":
            if not value.isdigit():
                return await message.answer("Необходимо указать число цифрами. Введите еще раз")
            elif int(value) < 1:
                return await message.answer("Цена должна быть положительным числом. Введите еще раз")
    cafe.update(f'{AdminEditFood.column} = {value}', where=f'id = {AdminEditFood.food_id}')
    change_text = f"TG_{tg_id} изменил значение [{AdminEditFood.column}] с [{AdminEditFood.current_value}] " \
                  f"на [{value}] у блюда ID_{AdminEditFood.food_id}"
    await add_log(change_text)

    for admin in await get_admins():
        await bot.send_message(admin, "Администратор " + change_text)

    await message.answer('Меню заведения', reply_markup=await kb_client_cafe_menu())

    await state.finish()

# ========================================================
#                      END EDIT FOOD
# ========================================================


# ====================== LOADING ======================
def register_handlers_storage_admin(dp: Dispatcher):
    dp.register_message_handler(cancel_button, Text(equals="отмена", ignore_case=True), state="*")
    dp.register_message_handler(cancel_button, commands=["отмена", "назад"], state="*")
    dp.register_callback_query_handler(admin_edit_food, Text(startswith="kea_"))
    dp.register_message_handler(admin_edit_food_reply, state=AdminEditFood.value)
