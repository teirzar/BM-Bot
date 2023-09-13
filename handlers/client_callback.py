from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageCantBeDeleted, BadRequest, MessageNotModified
from config import bot
from functions import add_log, get_tg_id, get_user_id, get_food_text, set_order, clear_basket, set_rating, get_admins
from functions import get_user_bonus, get_user_status, is_bonus_activated, update_user_bonus, get_current_discount
from functions import make_purchase, get_text_basket, get_order_text, get_prev_orders, cancel_order, get_order_info
from functions import decor_check_username, remake_order
from keyboards import kb_client_inline_menu, kb_client_inline_menu_info, kb_client_inline_basket_menu
from keyboards import kb_client_inline_order_menu, kb_client_inline_order_cancel_button
from keyboards import kb_client_inline_prev_orders_menu, kb_admin_order_inline_button


# =======================================
#                CAFE MENU
# =======================================

async def client_inline_menu(callback: types.CallbackQuery):
    """Функция-хэндлер клавиатуры kb_client_inline_menu"""
    user_id, tg_id = await get_user_id(callback), await get_tg_id(callback)
    cmd, *data = callback.data.split("_")[1:]
    is_new_message = False
    match cmd:

        case "current":
            food_id, type_food, current_id = data
            if food_id == current_id:
                error = "Данное блюдо уже выбрано. Вы можете посмотреть информацию; "
                error += ("добавить или отнять количество позиций; а также удалить товар из корзины."
                          if tg_id not in await get_admins() else
                          "изменить доступность товара или редактировать информацию о нем.")
                return await callback.answer(error, show_alert=True)
            text, cb_text = f"ID_{user_id} выбрал блюдо ID_{food_id}", "Выбор блюда."
            kb = await kb_client_inline_menu(type_food, tg_id, current_id=int(food_id))

        case "info":
            food_id = data[0]
            text, cb_text = f"ID_{user_id} открыл инфо о блюде ID_{food_id}", "Открываю информацию о товаре"
            text_new_message, image = await get_food_text(food_id)
            kb, is_new_message = await kb_client_inline_menu_info(food_id, tg_id), True

        case "food":
            food_id, cmd, type_food = data
            res = await set_order(user_id, food_id, cmd)
            if type(res) is str:
                return await callback.answer(res, show_alert=True)
            kb = await kb_client_inline_menu(type_food, tg_id, current_id=int(food_id))
            text = f"ID_{user_id} выбрал <{cmd}> блюдо ID_{food_id}"
            cb_text = "Добавлено!" if cmd == "plus" else "Удалено!"

    await add_log(text)

    try:
        await bot.send_photo(tg_id, photo=image, caption=text_new_message, reply_markup=kb, parse_mode='html') \
            if is_new_message else await callback.message.edit_reply_markup(reply_markup=kb)
    except MessageNotModified:
        pass

    return await callback.answer(cb_text)


async def client_inline_menu_info(callback: types.CallbackQuery):
    """Функция-хэндлер клавиатуры kb_client_inline_menu"""
    user_id, tg_id = await get_user_id(callback), await get_tg_id(callback)
    cmd, *data = callback.data.split("_")[1:]
    is_new_message, text_new_message = False, "text"
    match cmd:

        case 'like' | 'dislike':
            food_id = data[0]
            res = await set_rating(food_id, user_id, cmd)
            if res:
                return await callback.answer(res, show_alert=True)
            cb_text, text = f"Вы поставили {cmd}!", f"ID_{user_id} поставил <{cmd}> блюду ID_{food_id}"
            kb = await kb_client_inline_menu_info(food_id, tg_id)

        case 'plus' | 'minus':
            food_id = data[0]
            res = await set_order(user_id, food_id, cmd)
            if type(res) is str:
                return await callback.answer(res, show_alert=True)
            kb = await kb_client_inline_menu_info(food_id, tg_id)
            text = f"ID_{user_id} выбрал <{cmd}> блюдо ID_{food_id}"
            cb_text = "Добавлено!" if cmd == "plus" else "Удалено!"

        case 'open':
            typ = data[0]
            kb = await kb_client_inline_menu(40 if typ == "snack" else 60, tg_id)
            text, cb_text, is_new_message = f"ID_{user_id} открыл доп. меню <{typ}>", "Открываю новое меню", True
            text_new_message = "Выберите товар:"

    await add_log(text)

    try:
        await bot.send_message(tg_id, text=text_new_message, reply_markup=kb) if is_new_message else \
            await callback.message.edit_reply_markup(reply_markup=kb)
    except MessageNotModified:
        pass

    return await callback.answer(cb_text)

# =======================================
#              END CAFE MENU
# =======================================


# =======================================
#                 BASKET
# =======================================

async def client_inline_basket_menu(callback: types.CallbackQuery):
    """Функция-хэндлер клавиатуры kb_client_inline_basket"""
    user_id, tg_id = await get_user_id(callback), await get_tg_id(callback)
    cmd, *data = callback.data.split("_")[1:]
    is_new_message = False
    match cmd:

        case "info":
            food_id = data[0]
            text, cb_text = f"ID_{user_id} открыл инфо о блюде ID_{food_id}", "Открываю информацию о товаре"
            text_new_message, image = await get_food_text(food_id)
            kb, is_new_message = await kb_client_inline_menu_info(food_id, tg_id), True

        case "food":
            food_id, cmd = data
            res = await set_order(user_id, food_id, cmd)
            if type(res) is str:
                return await callback.answer(res, show_alert=True)
            text_new_message, kb = await get_text_basket(tg_id, user_id), await kb_client_inline_basket_menu(user_id)
            text = f"ID_{user_id} выбрал <{cmd}> блюдо ID_{food_id}"
            cb_text = "Добавлено!" if cmd == "plus" else "Удалено!"

    await add_log(text)

    try:
        await bot.send_photo(tg_id, photo=image, caption=text_new_message, reply_markup=kb, parse_mode='html') \
            if is_new_message else await callback.message.edit_text(text=text_new_message, reply_markup=kb)
    except MessageNotModified:
        pass

    return await callback.answer(cb_text)

# =======================================
#               END BASKET
# =======================================


# =======================================
#                 ORDER
# =======================================

@decor_check_username
async def client_inline_order_menu(callback: types.CallbackQuery):
    """Хэндлер клавиатуры kb_client_inline_order_menu"""
    user_id, tg_id = await get_user_id(callback), await get_tg_id(callback)
    cmd = callback.data.split("_")[1]
    match cmd:

        case "bonus":
            bonus, order_check = await get_user_bonus(user_id), await is_bonus_activated(user_id)
            if not bonus or order_check:
                txt_err = order_check if type(order_check) == str else "У вас нет бонусов или они были использованы!"
                return await callback.answer(txt_err, show_alert=True)

            res = await update_user_bonus(user_id)

            if type(res) == str:
                await callback.message.edit_text(res)
                return await callback.answer(res, show_alert=True)

            new_price, user_bonus, current_discount = res

            text = f"ID_{user_id} списал бонусы в количестве {current_discount} руб."
            cb_text = f"{current_discount} бонусов списаны!"

            new_text_message = await get_text_basket(tg_id, user_id, full=True)
            new_text_message += f"\nБонусный баланс: {user_bonus}\n" \
                                f"Скидка составила: {current_discount}\n" \
                                f"Новая цена: {new_price}"

            kb = await kb_client_inline_order_menu(user_id, user_bonus, current_discount)

        case "buy":
            res = await make_purchase(user_id, tg_id)
            if type(res) == str:
                return await callback.answer(res, show_alert=True)
            order_id = res[-1]
            for admin in await get_admins():
                await bot.send_message(admin,
                                       text=await get_order_text(user_id, res),
                                       reply_markup=await kb_admin_order_inline_button(order_id),
                                       )
            new_text_message = f"Заказ №{order_id} успешно создан и отправлен в заведение! " \
                               f"Вам будет начислен кэшбек после того, как Вы заберете заказ в заведении. " \
                               f"Когда заказ будет принят, Вам придет уведомление! " \
                               "Если у Вас возникнут вопросы по заказу, позвоните нам, либо заполните форму обратной " \
                               "связи в настройках в нашем боте.\n\nСпасибо, что выбрали нас!"
            text, cb_text = f"ID_{user_id} оформил заказ ID_{order_id}", "Отправляю заказ в заведение"
            kb = await kb_client_inline_order_cancel_button(order_id)

    await add_log(text)
    await callback.answer(cb_text)
    return await callback.message.edit_text(text=new_text_message, reply_markup=kb)


@decor_check_username
async def client_inline_order_cancel_button(callback: types.CallbackQuery):
    """Хэндлер кнопки отмены заказа kb_client_inline_order_cancel_button"""
    user_id, tg_id = await get_user_id(callback), await get_tg_id(callback)
    cmd, order_id = callback.data.split("_")[1:]
    kb = None
    match cmd:
        case "cancel":
            new_text_message = await cancel_order(order_id)
            await add_log(f'ID_{user_id} хочет отменить заказ ID_{order_id}')
            if not new_text_message:
                error = "Невозможно отменить заказ, который находится в корзине/приготовлен/завершен/отменен."
                return await callback.answer(error, show_alert=True)
            log_text, cb_text = "отменил", f"Отменяю заказ № {order_id}"
            for admin in await get_admins():
                await bot.send_message(admin, f'Пользователь ID_{user_id} отменил заказ ID_{order_id}!')

        case "reorder":
            await remake_order(order_id, user_id)
            log_text, cb_text = "повторил", f"Повторяю состав заказа № {order_id}"
            bonus, new_text_message = await get_user_bonus(user_id), await get_text_basket(tg_id, user_id, full=True)
            res = await get_user_status(user_id)
            if type(res) == str:
                return await callback.answer(res, show_alert=True)
            discount, status = res
            new_text_message += f"\nБонусный баланс: {bonus} бонусов\n" \
                                f"Уровень кэшбека при вашем статусе <{status}> составляет: {discount}%"
            current_discount = await get_current_discount(user_id)
            kb = await kb_client_inline_order_menu(user_id, bonus, current_discount)

    await callback.answer(cb_text)
    await add_log(f'ID_{user_id} {log_text} заказ ID_{order_id}')

    return await callback.message.edit_text(text=new_text_message, reply_markup=kb)


async def client_inline_prev_orders_menu(callback: types.CallbackQuery):
    """Хэндлер кнопки просмотра прошлого заказа kb_client_inline_prev_orders_menu"""
    user_id, tg_id = await get_user_id(callback), await get_tg_id(callback)
    order_id = callback.data.split("_")[1]
    new_text_message = await get_order_info(order_id)
    kb = await kb_client_inline_order_cancel_button(order_id, is_return=True)
    await add_log(f'ID_{user_id} просматривает информацию из архива о заказе ID_{order_id}')
    await callback.answer(f"Открываю заказ № {order_id}")
    return await callback.message.edit_text(text=new_text_message, reply_markup=kb)

# =======================================
#               END ORDER
# =======================================


# =======================================
#                 OTHER
# =======================================

async def cmd_close_inline_handler(callback: types.CallbackQuery):
    """Хэндлер кнопки закрытия клавиатуры"""
    try:
        await callback.message.delete()
    except MessageCantBeDeleted:
        try:
            return await callback.message.edit_text("Удалено")
        except BadRequest:
            return await callback.answer("Слишком старое сообщение, невозможно его удалить\n"
                                         "Удалите сообщение у себя в диалоге", show_alert=True)
    return await callback.answer("Закрыл")


async def client_inline_menu_button_support(callback: types.CallbackQuery):
    """Хэндлер общих вспомогательных кнопок на клавиатурах"""
    user_id, tg_id = await get_user_id(callback), await get_tg_id(callback)
    cmd, *data = callback.data.split("_")[1:]
    is_new_message = is_new_text = False
    match cmd:

        case "clear":
            type_food = data[0]
            cb_text = await clear_basket(user_id)
            if not cb_text:
                return await callback.answer("В Вашей корзине нет товаров!", show_alert=True)
            text = f"ID_{user_id} очистил корзину"
            if type_food:
                kb = await kb_client_inline_menu(type_food, tg_id)
            else:
                text_new_message, is_new_text = await get_text_basket(tg_id, user_id), True
                kb = await kb_client_inline_basket_menu(user_id)

        case "open":
            text, cb_text, is_new_message = f"ID_{user_id} открыл корзину", "Открываю корзину", True
            text_new_message = await get_text_basket(tg_id, user_id)
            kb = await kb_client_inline_basket_menu(user_id)

        case "order":
            text, cb_text = f"ID_{user_id} зашел в оформление заказа", "Оформление заказа"
            bonus, text_new_message = await get_user_bonus(user_id), await get_text_basket(tg_id, user_id, full=True)
            res = await get_user_status(user_id)
            if type(res) == str:
                return await callback.answer(res, show_alert=True)
            discount, status = res
            text_new_message += f"\nБонусный баланс: {bonus} бонусов\n" \
                                f"Уровень кэшбека при вашем статусе <{status}> составляет: {discount}%"
            current_discount = await get_current_discount(user_id)
            kb, is_new_message = await kb_client_inline_order_menu(user_id, bonus, current_discount), True

        case "show":
            return await callback.answer("")

        case "return":
            text, cb_text = f"ID_{user_id} вернулся в архив заказов", "Архив заказов"
            text_new_message = await get_prev_orders(user_id, tg_id)
            is_new_text, kb = True, await kb_client_inline_prev_orders_menu(user_id)

    await add_log(text)
    await callback.answer(cb_text)
    if is_new_message:
        return await bot.send_message(tg_id, text=text_new_message, reply_markup=kb)
    elif is_new_text:
        return await callback.message.edit_text(text=text_new_message, reply_markup=kb)
    return await callback.message.edit_reply_markup(reply_markup=kb)

# =======================================
#               END OTHER
# =======================================


# ====================== LOADING ======================
def register_inline_handlers_client(dp: Dispatcher):
    """Регистрация хэндлеров"""
    dp.register_callback_query_handler(cmd_close_inline_handler, Text(equals="close_inline_handler"))
    dp.register_callback_query_handler(client_inline_menu, Text(startswith="cm_"))
    dp.register_callback_query_handler(client_inline_menu_info, Text(startswith="cmi_"))
    dp.register_callback_query_handler(client_inline_menu_button_support, Text(startswith="bs_"))
    dp.register_callback_query_handler(client_inline_basket_menu, Text(startswith="cb_"))
    dp.register_callback_query_handler(client_inline_order_menu, Text(startswith="om_"))
    dp.register_callback_query_handler(client_inline_order_cancel_button, Text(startswith="oc_"))
    dp.register_callback_query_handler(client_inline_prev_orders_menu, Text(startswith="order_"))
