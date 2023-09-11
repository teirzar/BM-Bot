from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove
from aiogram import types, Dispatcher
from functions import add_log, get_time, get_user_id, get_tg_id, get_admins, get_text_message, get_user_bonus
from functions import get_current_discount, get_text_basket
from config import bot, users, messages, orders
from keyboards import kb_client_settings_menu, kb_admin_answer_message_inline_button, kb_cancel_button
from keyboards import kb_client_cafe_menu, kb_admin_yes_no_button, kb_client_inline_order_menu


# ========================================================
#                        MESSAGE
# ========================================================

class ClientWriteMessage(StatesGroup):
    new_message = State()


async def client_write_message(message: types.Message):
    user_id = await get_user_id(message)
    await ClientWriteMessage.new_message.set()
    await add_log(f"ID_{user_id} зашел в форму отзывов")
    reply_msg = "Оставьте нам свой отзыв/пожелание/вопрос/предложение. Форма обратной связи.\n" \
                "Для выхода из формы - напишите 'Отмена'."
    await message.reply(reply_msg, reply_markup=await kb_cancel_button())


async def client_write_message_reply(message: types.Message, state: FSMContext):
    user_id = await get_user_id(message)
    tg_id = await get_tg_id(message)
    async with state.proxy() as data:
        data["text"] = message.text
    if len(data['text']) == 0:
        await state.finish()
        text_error = "Нельзя оставлять пустое сообщение"
        return await message.reply(text_error, reply_markup=await kb_client_settings_menu(), parse_mode="html")
    now = await get_time()
    user_message = data['text'].replace('"', "''")
    messages.write('tg_id', 'message', 'time', values=f'{tg_id}, "{user_message}", "{now}"')
    message_id = messages.print_table('id', where=f'tg_id = {tg_id}', order_by='id DESC LIMIT 1')[0][0]
    await message.reply(f"Сообщение отправлено! Спасибо!", reply_markup=await kb_client_settings_menu())
    adm_kb = await kb_admin_answer_message_inline_button(message_id)
    for admin in await get_admins():
        await bot.send_message(admin, f"Новый отзыв\n{await get_text_message(message_id)}", reply_markup=adm_kb)
    await add_log(f"ID_{user_id} Отправил отзыв ID_{message_id}")
    await state.finish()


# ========================================================
#                      END MESSAGE
# ========================================================


# ========================================================
#                     EDIT PROFILE
# ========================================================

class ClientEditProfile(StatesGroup):
    new_value = State()
    column = None
    user_id = None


async def client_edit_profile(message: types.Message):
    column = message.text.split()[-1].lower()
    if column not in ("телефон", "имя"):
        return await message.reply("Можно изменить только телефон или имя!")
    ClientEditProfile.column = 'name' if column == 'имя' else 'phone'
    ClientEditProfile.user_id = await get_user_id(message)
    await ClientEditProfile.new_value.set()
    await add_log(f"ID_{ClientEditProfile.user_id} зашел в форму изменения [{column}]")
    text = "Имя должно быть от 2 до 20 символов\n" if column == 'имя' else \
        "Телефон должен быть записан в формате 7XXXXXXXXXX, где Х - это цифра от 0 до 9 (включая первую 7)\n"
    await message.reply(text + "Для выхода из формы - напишите 'Отмена'.", reply_markup=await kb_cancel_button())


async def client_edit_profile_reply(message: types.Message, state: FSMContext):
    user_id = ClientEditProfile.user_id
    async with state.proxy() as data:
        data["value"] = message.text
    value = data["value"].replace('"', "''").strip("+")
    log_error_text = f"ID_{user_id} не удалось изменить [{ClientEditProfile.column}] на [{value}]"
    kb = await kb_client_settings_menu()

    if ClientEditProfile.column == 'name':
        if len(value) not in range(2, 21):
            await add_log(log_error_text)
            await message.reply("Имя не должно быть менее 2-х и более 20-ти символов", reply_markup=kb)
            return await state.finish()

    elif ClientEditProfile.column == 'phone':
        if not value.isdigit() or len(value) != 11:
            await add_log(log_error_text)
            text = "(неверное количество цифр)" if value.isdigit() else "(не числовые значения)"
            await message.reply(f'Введенная информация содержит некорректные данные {text}', reply_markup=kb)
            return await state.finish()

    users.update(f'{ClientEditProfile.column} = "{value}"', where=f'id = {user_id}')
    log_text = f"ID_{user_id} изменил [{ClientEditProfile.column}] на [{value}]"
    await add_log(log_text)
    await message.reply(f"Успешно изменено!\nНовое значение: <b>{value}</b>", parse_mode='html', reply_markup=kb)
    for admin in await get_admins():
        await bot.send_message(admin, f"Пользователь {log_text}")
    return await state.finish()


# ========================================================
#                    END EDIT PROFILE
# ========================================================


# ========================================================
#                        ORDERS
# ========================================================
class ClientWriteComment(StatesGroup):
    new_comment = State()
    confirm = State()
    tg_id = None
    user_id = None
    order_id = None


async def client_write_comment(callback: types.CallbackQuery):
    ClientWriteComment.tg_id, ClientWriteComment.user_id = await get_tg_id(callback), await get_user_id(callback)
    try:
        order_id = orders.print_table('id', where=f'user_id = {ClientWriteComment.user_id} and status = 0')[0][0]
    except IndexError:
        kb = await kb_client_cafe_menu()
        return await bot.send_message(ClientWriteComment.tg_id, "Заказ не найден, повторите попытку", reply_markup=kb)
    ClientWriteComment.order_id = order_id
    await ClientWriteComment.new_comment.set()
    await add_log(f"ID_{ClientWriteComment.user_id} зашел в форму написания комментария к заказу")
    reply_msg = "Для выхода из формы - напишите '<code>Отмена</code>'.\n" \
                "Оставьте комментарий к заказу:"
    await bot.send_message(ClientWriteComment.tg_id, reply_msg, reply_markup=ReplyKeyboardRemove(), parse_mode='html')
    await callback.answer("Напишите комментарий к заказу.")


async def client_write_comment_reply(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["text"] = message.text.replace('"', "''")

    if len(data['text']) == 0:
        await state.finish()
        text_error = "Нельзя оставлять пустое сообщение."
        return await message.answer(text_error, reply_markup=await kb_client_cafe_menu(), parse_mode="html")

    text_msg = f"Ваш комментарий:\n\n{data['text']}\n\nПроверьте правильность ввода и нажмите (напишите) " \
               f"'<code>Да</code>' - для отправки, '<code>Нет</code>' - отменить"
    await message.reply(text_msg, reply_markup=await kb_admin_yes_no_button(), parse_mode='html')
    await add_log(f"ID_{ClientWriteComment.user_id} написал комментарий к заказу ID_{ClientWriteComment.order_id}")
    await ClientWriteComment.next()


async def client_write_comment_confirm_reply(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["confirm"] = message.text.lower().replace('"', "''").strip("'")
    kb = await kb_client_cafe_menu()

    if data["confirm"] == "нет":
        log_text, msg_text = "отменил комментарий", 'Успешно отменено'

    elif data["confirm"] == "да":
        orders.update(f'''comment = "{data['text']}"''', where=f'id = {ClientWriteComment.order_id}')
        log_text, msg_text = "оставил комментарий", f"Комментарий '{data['text']}' успешно добавлен к заказу."
        tg_id, user_id, is_inline_message = ClientWriteComment.tg_id, ClientWriteComment.user_id, True
        text_new_message = await get_text_basket(tg_id, user_id, full=True)
        bonus, discount = await get_user_bonus(user_id), await get_current_discount(user_id)
        kb = await kb_client_inline_order_menu(user_id, bonus, discount)
        await bot.send_message(tg_id, text_new_message, reply_markup=kb)
        kb = ReplyKeyboardRemove()

    else:
        log_text, msg_text = "ошибка в добавлении комментария", "Необходимо подтвердить или отменить отправку."

    await add_log(f"ID_{ClientWriteComment.user_id} {log_text} к заказу ID_{ClientWriteComment.order_id}")
    await message.answer(msg_text, reply_markup=kb)
    return await state.finish()

# ========================================================
#                      END ORDERS
# ========================================================


# ====================== LOADING ======================
def register_handlers_storage_client(dp: Dispatcher):
    dp.register_message_handler(client_edit_profile, Text(startswith="⚙ Изменить "))
    dp.register_message_handler(client_edit_profile_reply, state=ClientEditProfile.new_value)
    dp.register_message_handler(client_write_message, Text(equals="✏️ Написать нам"))
    dp.register_message_handler(client_write_message_reply, state=ClientWriteMessage.new_message)
    dp.register_callback_query_handler(client_write_comment, Text(equals="write_comment"))
    dp.register_message_handler(client_write_comment_reply, state=ClientWriteComment.new_comment)
    dp.register_message_handler(client_write_comment_confirm_reply, state=ClientWriteComment.confirm)
