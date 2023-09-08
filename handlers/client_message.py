from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from config import bot, HELP_MESSAGE, START_MESSAGE, ABOUT_MESSAGE, users
from functions import add_log, get_tg_id, get_admins, get_user_id, get_prev_orders, get_profile_text, get_type_food_id
from keyboards import kb_client_main_menu, kb_client_settings_menu, kb_client_cafe_menu, kb_client_cafe_menu_option
from keyboards import kb_client_inline_menu, kb_client_inline_prev_orders_menu


# =======================================
#               MAIN MENU
# =======================================

async def cmd_client_start_menu(message: types.Message):
    """Стартовое меню, запись аккаунта в БД"""
    tg_id = await get_tg_id(message)
    if (tg_id, ) not in users.print_table('tg_id'):
        username, name = message["from"].username, message["from"].first_name
        text = f" Новый пользователь! TG: {username}; ID_{tg_id}"
        users.write('tg_id', 'username', 'name', values=f'{tg_id}, "{username}", "{name}"')
        await add_log(text)
        [await bot.send_message(admin, text) for admin in await get_admins()]
        return await bot.send_message(tg_id, START_MESSAGE, parse_mode='html', reply_markup=await kb_client_main_menu())
    await add_log(f"ID_{await get_user_id(message)} зашел в главное меню")
    return await bot.send_message(tg_id, "Главное меню", reply_markup=await kb_client_main_menu())

# =======================================
#              END MAIN MENU
# =======================================


# =======================================
#                STATIC
# =======================================
async def cmd_client_static_menu(message: types.Message):
    """Функция для элементов не требующих вызов подменю"""
    user_id, tg_id = await get_user_id(message), await get_tg_id(message)
    new_kb = False

    match message.text:
        case "❓ Помощь" | "/help":
            log_text, text = "помощь", HELP_MESSAGE
        case "💼 О нас" | "/about":
            log_text, text = "информацию о заведении", ABOUT_MESSAGE
            await bot.send_location(tg_id, latitude=60.16347184315989, longitude=30.355113890416416)
        case "👤 Мой профиль" | "/profile":
            log_text, text = "профиль", await get_profile_text(user_id)
        case "☎ Позвонить" | "/call":
            log_text, text = "номер телефона заведения", "Наш номер телефона: +12345678901"
        case "🧾 Мои заказы" | "/orders":
            log_text, text = "архив заказов", await get_prev_orders(user_id, tg_id)
            new_kb, kb = True, await kb_client_inline_prev_orders_menu(user_id)

    await add_log(f"ID_{user_id} просматривает {log_text}")
    return await bot.send_message(tg_id, text, parse_mode='html') if not new_kb else \
        await bot.send_message(tg_id, text, parse_mode='html', reply_markup=kb)


async def cmd_client_static_submenu(message: types.Message):
    """Функция для вызова подменю основных кнопок меню"""
    user_id, tg_id = await get_user_id(message), await get_tg_id(message)

    match message.text:
        case "🍔 Меню ресторана 🌯" | "/menu" | "⬅️ Назад":
            text, kb = "Меню ресторана", await kb_client_cafe_menu()
        case "⚙ Настройки" | "/settings":
            text, kb = "Настройки", await kb_client_settings_menu()

    await add_log(f"ID_{user_id} открыл {text}")
    return await bot.send_message(tg_id, text, reply_markup=kb)


# =======================================
#               END STATIC
# =======================================


# =======================================
#               CAFE MENU
# =======================================

async def cmd_client_cafe_menu_option(message: types.Message):
    """Функция для вызова уточнения выбора в меню заведения"""
    user_id, tg_id = await get_user_id(message), await get_tg_id(message)
    match message.text:
        case "🌯 Шаверма":
            text = "Обратите внимание!\n" \
                   "Куриное филе в шавермах нашего заведения маринуется поварами и готовится на гриле.\n" \
                   "Всегда свежее филе готовится специально для вас в момент заказа, " \
                   "мы не используем вертел, где мясо портится часами на открытом воздухе.\n" \
                   "Попробуйте сами и убедитесь в неповторимом вкусе!"
            b1, b2 = "🥗 Шаверма на тарелке", "🌯 Шаверма в лаваше"
        case "🌭 Хот-Дог":
            text = "Вы можете заказать Хот-дог как в стандартной булочке, так и в лаваше."
            b1, b2 = "🌭 Хот-Дог стандартный", "🫔 Хот-Дог в лаваше"
        case "🥤Напитки":
            text = "Выберите тип напитка."
            b1, b2 = "☕Горячие напитки", "🥤Холодные напитки"
    await add_log(f"ID_{user_id} зашел в подвыбор меню ресторана в категории {message.text[1:].strip()}")
    await bot.send_message(tg_id, text, reply_markup=await kb_client_cafe_menu_option(b1, b2))


async def cmd_client_cafe_menu(message: types.Message):
    """Функция для вызова инлайн меню товарных позиций"""
    user_id, tg_id = await get_user_id(message), await get_tg_id(message)
    text = f"Вы выбрали {message.text}. Далее выберите товарную позицию:"
    food_type = await get_type_food_id(message.text)
    await add_log(f"ID_{user_id} выбрал {message.text[1:]}")
    await bot.send_message(tg_id, text, reply_markup=await kb_client_inline_menu(food_type, tg_id))


# =======================================
#             END CAFE MENU
# =======================================


# ====================== LOADING ======================
def register_handlers_client(dp: Dispatcher):
    """Регистрация хэндлеров"""
    dp.register_message_handler(cmd_client_start_menu, commands=['start'])
    dp.register_message_handler(cmd_client_start_menu, Text(equals='🏠 На главную'))

    dp.register_message_handler(cmd_client_static_menu, commands=['help', 'about', 'profile', 'call', 'orders'])
    dp.register_message_handler(cmd_client_static_menu, Text(equals='❓ Помощь'))
    dp.register_message_handler(cmd_client_static_menu, Text(equals='💼 О нас'))
    dp.register_message_handler(cmd_client_static_menu, Text(equals='☎ Позвонить'))
    dp.register_message_handler(cmd_client_static_menu, Text(equals='👤 Мой профиль'))
    dp.register_message_handler(cmd_client_static_menu, Text(equals="🧾 Мои заказы"))

    dp.register_message_handler(cmd_client_static_submenu, commands=['menu', 'settings'])
    dp.register_message_handler(cmd_client_static_submenu, Text(equals="🍔 Меню ресторана 🌯"))
    dp.register_message_handler(cmd_client_static_submenu, Text(equals="⬅️ Назад"))
    dp.register_message_handler(cmd_client_static_submenu, Text(equals="⚙ Настройки"))

    dp.register_message_handler(cmd_client_cafe_menu, Text(equals="🍔 Бургер"))
    dp.register_message_handler(cmd_client_cafe_menu, Text(equals="🌱 Vegan"))
    dp.register_message_handler(cmd_client_cafe_menu, Text(equals="🍟 Закуски"))
    dp.register_message_handler(cmd_client_cafe_menu, Text(equals="🥗 Шаверма на тарелке"))
    dp.register_message_handler(cmd_client_cafe_menu, Text(equals="🌯 Шаверма в лаваше"))
    dp.register_message_handler(cmd_client_cafe_menu, Text(equals="🌭 Хот-Дог стандартный"))
    dp.register_message_handler(cmd_client_cafe_menu, Text(equals="🫔 Хот-Дог в лаваше"))
    dp.register_message_handler(cmd_client_cafe_menu, Text(equals="☕Горячие напитки"))
    dp.register_message_handler(cmd_client_cafe_menu, Text(equals="🥤Холодные напитки"))

    dp.register_message_handler(cmd_client_cafe_menu_option, Text(equals="🌯 Шаверма"))
    dp.register_message_handler(cmd_client_cafe_menu_option, Text(equals="🌭 Хот-Дог"))
    dp.register_message_handler(cmd_client_cafe_menu_option, Text(equals="🥤Напитки"))



