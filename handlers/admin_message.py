from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from config import bot
from functions import decor_private, add_log, set_admin, get_admins, get_owner, show_admins, get_tg_id, give_me_admin
from keyboards import kb_admin_main_menu, kb_admin_current_orders_inline_menu


# =======================================
#            MAIN ADMIN MENU
# =======================================

@decor_private
async def cmd_admin_main_menu(message: types.Message):
    """Функция вызова меню /admin"""
    return await message.answer("Панель администратора", reply_markup=await kb_admin_main_menu())

# =======================================
#           END MAIN ADMIN MENU
# =======================================

@decor_private
async def cmd_admin_show_order(message: types.Message):
    """Функция для просмотра активных заказов"""
    return await message.answer("Выберите нужный заказ", reply_markup=await kb_admin_current_orders_inline_menu())


# =======================================
#                 OTHER
# =======================================

@decor_private
async def cmd_make_admin(message: types.Message):
    """Функция для записи нового админа"""
    tg_id = await get_tg_id(message)
    data = message.text.split()
    res = await set_admin(data)
    await add_log(f'TG_{tg_id} пытается назначить администратора командой [{message.text}]')
    if type(res) == str:
        return await message.answer(res)
    await add_log(f"TG_{tg_id} назначил администратора TG_{res}")
    for admin in await get_admins():
        await bot.send_message(admin, f"Админ TG {tg_id} назначил админа TG {res}")
    await bot.send_message(res, "Вы назначены администратором в боте BURGERMAKER.\nПоздравляем!\nАдминка: /admin")
    return await message.answer("Админ назначен")


@decor_private
async def cmd_show_admins(message: types.Message):
    """Функция для вывода в сообщение всех админов в боте"""
    tg_id = await get_tg_id(message)
    await add_log(f'TG_{tg_id} просматривает текущих администраторов')
    return await message.answer(await show_admins())


@decor_private
async def cmd_delete_admin(message: types.Message):
    """Функция для снятия админов, доступно только владельцу"""
    tg_id = await get_tg_id(message)
    await add_log(f"TG_{tg_id} пытается снять администратора командой [{message.text}]")
    if tg_id != get_owner():
        return await message.answer("Вы не владелец, чтобы удалять админов.")
    data = message.text.split()
    res = await set_admin(data, delete=True)
    if type(res) == str:
        return await message.answer(res)
    await add_log(f"TG_{tg_id} снял администратора TG_{res}")
    await bot.send_message(res, "Администрирование аннулировано.")
    return await message.answer("Админ снят.")


async def cmd_give_me_admin(message: types.Message):
    """Функция для получения админки, если вдруг она была снята"""
    tg_id = await get_tg_id(message)
    await add_log(f"TG_{tg_id} использовал команду /givemeadmin")
    if tg_id == get_owner():
        if tg_id in await get_admins():
            return await message.answer("Вы уже администратор.")
        await give_me_admin()
        await add_log(f"TG_{tg_id} назначил себя администратором.")
        return await message.answer("Вы назначены администратором.")
    return

# =======================================
#               END OTHER
# =======================================


# ====================== LOADING ======================
def register_handlers_admin(dp: Dispatcher):
    """Регистрация хэндлеров"""
    dp.register_message_handler(cmd_admin_main_menu, commands=['admin'])

    dp.register_message_handler(cmd_make_admin, commands=['makeadmin'])
    dp.register_message_handler(cmd_show_admins, commands=['showadmins'])
    dp.register_message_handler(cmd_delete_admin, commands=['deleteadmin'])
    dp.register_message_handler(cmd_give_me_admin, commands=['givemeadmin'])

    dp.register_message_handler(cmd_admin_show_order, Text(equals="📂 Заказы"))
