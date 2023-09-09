from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# =======================================
#            MAIN ADMIN MENU
# =======================================

async def kb_admin_main_menu():
    """Меню администратора"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    b1 = KeyboardButton("📂Заказы")
    b2 = KeyboardButton("💬Рассылка")
    b3 = KeyboardButton("🗄Обращения")
    b4 = KeyboardButton("/start")
    kb.add(b1, b2, b3, b4)
    return kb

# =======================================
#           END MAIN ADMIN MENU
# =======================================
