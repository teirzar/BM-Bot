from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.exceptions import BotBlocked
from config import bot, messages, users, cafe, orders
from functions import get_tg_id, add_log, get_current_food_value, get_user_id, decor_private, get_time, send_to_admins
from keyboards import kb_cancel_button, kb_client_main_menu, kb_client_cafe_menu, kb_admin_yes_no_button
from keyboards import kb_admin_main_menu


# ========================================================
#                        CANCEL
# ========================================================

async def cancel_button(message: types.Message, state: FSMContext):
    """Функция отмены машины состояний"""
    tg_id = await get_tg_id(message)
    user_id = await get_user_id(message)
    current_state = await state.get_state()
    if current_state is None:
        return
    await add_log(f"ID_{user_id}: [Отмена {current_state}]")
    await bot.send_message(tg_id, f"Отменено.", reply_markup=await kb_client_main_menu(tg_id))
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
    await send_to_admins("Администратор " + change_text)
    await message.answer('Меню заведения', reply_markup=await kb_client_cafe_menu())
    await state.finish()

# ========================================================
#                      END EDIT FOOD
# ========================================================


# ========================================================
#                        MAILING
# ========================================================
class AdminMailing(StatesGroup):
    """Рассылка сообщений пользователям"""
    text = State()
    confirm = State()
    message_id = None


@decor_private
async def admin_mailing(message: types.Message):
    tg_id = await get_tg_id(message)
    await AdminMailing.text.set()
    await add_log(f"TG_{tg_id} зашел в меню ввода сообщения всем пользователям")
    msg_text = "Напишите сообщение, которое нужно отправить всем пользователям, у которых включены уведомления\n" \
               "Чтобы выйти из формы отправки - напишите <code>Отмена</code>"
    await message.reply(msg_text, reply_markup=ReplyKeyboardRemove(), parse_mode='html')


async def admin_mailing_reply(message: types.Message, state: FSMContext):
    tg_id = await get_tg_id(message)
    async with state.proxy() as data:
        data["text"] = message.text.replace('"', "''")
    messages.write('adm_id', 'message', values=f'''{tg_id}, "{data['text']}"''')
    AdminMailing.message_id = messages.print_table('id', where=f'adm_id = {tg_id}', order_by='id DESC LIMIT 1')[0][0]
    await add_log(f"TG_{tg_id} сделал запись сообщения для пользователей ID_{AdminMailing.message_id}")
    msg_text = f"Проверьте правильность ввода:\n\n{data['text']}\n\n" \
               f"<code>Да</code> - для отправки, <code>Нет</code> - отменить"
    await message.answer(msg_text, reply_markup=await kb_admin_yes_no_button(), parse_mode='html')
    await AdminMailing.next()


async def admin_mailing_confirm_reply(message: types.Message, state: FSMContext):
    tg_id = await get_tg_id(message)
    async with state.proxy() as data:
        data["confirm"] = message.text.lower().replace('"', "''").strip("'")

    if data["confirm"] == "нет":
        log_text, msg_text = "отменил сообщение", 'Успешно отменено'

    elif data["confirm"] == "да":
        messages.update(f'answer_time = "{await get_time()}"', where=f'id = {AdminMailing.message_id}')
        all_users = [tg[0] for tg in users.print_table('tg_id', where=f'notification = 1')]
        errors = ""

        for user in all_users:
            try:
                await bot.send_message(user, data['text'])
            except BotBlocked:
                errors += f"TG_{user}, "
        log_text = "отправил сообщение"
        number = len(all_users) - len(errors.split())
        msg_text = f'Сообщение успешно разослано {number} пользователям\nОшибки при отправке: {errors}'

    else:
        log_text, msg_text = "ошибка в отправке сообщения", "Необходимо подтвердить или отменить отправку."

    await add_log(f"TG_{tg_id} {log_text} ID_{AdminMailing.message_id} всем пользователям")
    await message.answer(msg_text, reply_markup=await kb_admin_main_menu())
    return await state.finish()


# ========================================================
#                      END MAILING
# ========================================================


# ========================================================
#                     MESSAGE TO USER
# ========================================================
class AdminWriteToUser(StatesGroup):
    message = State()
    cmd = None
    user_tg_id = None
    user_id = None
    message_id = None
    user_message = None


async def admin_write_to_user(callback: types.CallbackQuery):
    cmd, obj_id = callback.data.split("_")[2:]
    admin_tg_id = await get_tg_id(callback)
    kb = await kb_cancel_button()
    match cmd:

        case "order":
            user_id = orders.print_table('user_id', where=f'id = {obj_id}')[0][0]
            res = users.print_table('tg_id', 'phone', 'username', 'name', where=f'id = {user_id}')
            user_tg_id, phone, username, name = res[0]
            log_text = f"TG_{admin_tg_id} хочет отправить сообщение пользователю ID_{user_tg_id} из заказа ID_{obj_id}"
            reply_msg = f"<b>Пользователь ID {user_id}.</b>\nИмя: {name}\nТелеграм: @{username}\nТелефон: {phone}\n\n" \
                        f"Напишите сообщение пользователю, если необходимо."
            cb_msg = "Открываю форму сообщения пользователю."

        case "message":
            res = messages.print_table('tg_id', 'message', 'adm_message', where=f'id = {obj_id}')[0]
            user_tg_id, user_message, adm_message = res
            AdminWriteToUser.message_id, AdminWriteToUser.user_message = obj_id, user_message
            if adm_message:
                err_msg, kb = "На это сообщение уже был дан ответ", await kb_admin_main_menu()
                await bot.send_message(admin_tg_id, f"{err_msg}:\n\n{adm_message}", reply_markup=kb)
                return await callback.answer(err_msg, show_alert=True)
            user_id = await get_user_id(user_tg_id, is_tg_id=True)
            log_text = f"TG_{admin_tg_id} хочет ответить пользователю ID_{user_tg_id} на сообщение ID_{obj_id}"
            reply_msg = f"Сообщение от пользователя ID_{user_id}, TG_{user_tg_id}:\n\n[{user_message}].\n\n" \
                        f"Напишите ответ на данное сообщение пользователю ID_{user_tg_id}"
            cb_msg = "Введите ответ пользователю на обращение."

    AdminWriteToUser.user_tg_id, AdminWriteToUser.user_id, AdminWriteToUser.cmd = user_tg_id, user_id, cmd
    reply_msg += "\n\nНапишите '<code>Отмена</code>', чтобы выйти из формы."
    await AdminWriteToUser.message.set()
    await add_log(log_text)
    await bot.send_message(admin_tg_id, reply_msg, reply_markup=kb, parse_mode='html')
    await callback.answer(cb_msg)


async def admin_write_to_user_reply(message: types.Message, state: FSMContext):
    adm_tg_id = await get_tg_id(message)
    async with state.proxy() as data:
        data["text"] = message.text.replace('"', "''")

    if len(data['text']) == 0:
        await state.finish()
        text_error = "Нельзя отправить пустое сообщение."
        return await message.answer(text_error, reply_markup=ReplyKeyboardRemove())

    now = await get_time()
    if AdminWriteToUser.cmd == "order":
        messages.write('tg_id', 'adm_id', 'adm_message', 'answer_time',
                       values=f'''{AdminWriteToUser.user_tg_id}, {adm_tg_id}, "{data['text']}", "{now}"''')
        log_text, msg_text = "отправил сообщение", f"Вам сообщение от администрации:\n{data['text']}"
    else:
        messages.update(f'''adm_id = {adm_tg_id}, adm_message = "{data['text']}", answer_time = "{now}"''',
                        where=f'id = {AdminWriteToUser.message_id}')
        log_text = f"ответил на сообщение ID_{AdminWriteToUser.message_id}"
        msg_text = f"На ваше обращение №{AdminWriteToUser.message_id} с текстом: [{AdminWriteToUser.user_message}]\n" \
                   f"\nБыл дан ответ от администрации:\n[{data['text']}]"

    log_msg = f"Администратор TG_{adm_tg_id} {log_text} пользователю ID_{AdminWriteToUser.user_id}"
    await send_to_admins(log_msg + f":\n\n{data['text']}")

    await bot.send_message(AdminWriteToUser.user_tg_id, msg_text)
    await message.answer("Сообщение было отправлено пользователю", reply_markup=await kb_admin_main_menu())
    await add_log(log_msg)
    await state.finish()

# ========================================================
#                    END MESSAGE TO USER
# ========================================================


# ====================== LOADING ======================
def register_handlers_storage_admin(dp: Dispatcher):
    dp.register_message_handler(cancel_button, Text(equals="отмена", ignore_case=True), state="*")
    dp.register_message_handler(cancel_button, commands=["отмена", "назад"], state="*")
    dp.register_callback_query_handler(admin_edit_food, Text(startswith="kea_"))
    dp.register_message_handler(admin_edit_food_reply, state=AdminEditFood.value)
    dp.register_message_handler(admin_mailing, Text(equals="💬Рассылка"))
    dp.register_message_handler(admin_mailing_reply, state=AdminMailing.text)
    dp.register_message_handler(admin_mailing_confirm_reply, state=AdminMailing.confirm)
    dp.register_callback_query_handler(admin_write_to_user, Text(startswith="write_user_"))
    dp.register_message_handler(admin_write_to_user_reply, state=AdminWriteToUser.message)

