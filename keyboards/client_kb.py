from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# =======================================
#               MAIN MENU
# =======================================

async def kb_client_main_menu():
    """Главное меню"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton("🍔 Меню ресторана 🌯")
    b2 = KeyboardButton("👤 Мой профиль")
    b3 = KeyboardButton("🧾 Мои заказы")
    b4 = KeyboardButton("❓ Помощь")
    b5 = KeyboardButton("⚙ Настройки")
    b6 = KeyboardButton("💼 О нас")
    b7 = KeyboardButton("☎ Позвонить")
    kb.add(b1).row(b2, b3).row(b4, b5).row(b6, b7)
    return kb

# =======================================
#              END MAIN MENU
# =======================================

