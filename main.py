from aiogram import executor
from functions import add_log


async def on_startup(_):
    await add_log("!! Бот запущен !!")
    print("Бот запущен")


if __name__ == "__main__":
    from config import dp
    from handlers import register_handlers_client

    register_handlers_client(dp)
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
