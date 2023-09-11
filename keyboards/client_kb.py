from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from functions import get_admins


# =======================================
#               MAIN MENU
# =======================================

async def kb_client_main_menu(tg_id):
    """Главное меню"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton("🍔 Меню ресторана 🌯")
    b2 = KeyboardButton("👤 Мой профиль")
    b3 = KeyboardButton("🧾 Мои заказы")
    b4 = KeyboardButton("❓ Помощь")
    b5 = KeyboardButton("⚙ Настройки")
    b6 = KeyboardButton("💼 О нас")
    b7 = KeyboardButton("☎ Позвонить")
    b8 = KeyboardButton("/admin")
    kb.add(b1).row(b2, b3).row(b4, b5).row(b6, b7)
    if tg_id in await get_admins():
        kb.add(b8)
    return kb

# =======================================
#              END MAIN MENU
# =======================================


# =======================================
#               CAFE MENU
# =======================================
async def kb_client_cafe_menu():
    """Главное меню заведения"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton("🍔 Бургер")
    b2 = KeyboardButton("🌯 Шаверма")
    b3 = KeyboardButton("🌭 Хот-Дог")
    b4 = KeyboardButton("🌱 Vegan")
    b5 = KeyboardButton("🍟 Закуски")
    b6 = KeyboardButton("🥤Напитки")
    b7 = KeyboardButton("🏠 На главную")
    kb.row(b1, b2, b3).add(b4, b5, b6).add(b7)
    return kb


async def kb_client_cafe_menu_option(b1, b2):
    """Подменю, выбор категории в меню заведения"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1, b2 = KeyboardButton(b1), KeyboardButton(b2)
    b3 = KeyboardButton("⬅️ Назад")
    b4 = KeyboardButton("🏠 На главную")
    kb.add(b1).add(b2).row(b3, b4)
    return kb


# =======================================
#              END CAFE MENU
# =======================================


# =======================================
#                SETTINGS
# =======================================

async def kb_client_settings_menu():
    """Меню настроек"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton("⚙ Изменить телефон")
    b2 = KeyboardButton("⚙ Изменить имя")
    b3 = KeyboardButton("✏️ Написать нам")
    b4 = KeyboardButton("🔔 Уведомления")
    b5 = KeyboardButton("🏠 На главную")
    kb.row(b1, b2).add(b3).add(b4, b5)
    return kb

# =======================================
#               END SETTINGS
# =======================================


# =======================================
#                 OTHER
# =======================================
async def kb_cancel_button():
    """Кнопка отмена, для выхода из вводов"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    return kb.add(KeyboardButton("Отмена"))

# =======================================
#               END OTHER
# =======================================
