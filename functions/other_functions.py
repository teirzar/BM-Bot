from datetime import datetime


# current time
async def get_time() -> str:
    """Возвращает строку времени в формате ГГГГ-ММ-ДД ЧЧ:ММ"""
    return datetime.now().strftime("%Y-%m-%d %H:%M")


async def add_log(string) -> None:
    """Функция логирования.
    Вносит в txt файл данные в формате 'Время: событие' """
    with open('logs/log.txt', 'a') as log:
        text = f'{await get_time()}: {string}\n'
        log.write(text)


def get_token() -> str:
    """Функция читает файл key.txt в директории private.
    Внести в него свой токен!"""
    with open('private/key.txt', 'r') as file:
        token = file.readline()
        return token


def get_owner() -> int:
    """Читает файл owner.txt в директории private.
    Внести Telegram id владельца бота!
    Чтобы узнать ID, если бот работает - команда /myid"""
    with open('private/key.txt', 'r') as file:
        owner = file.readline()
        return int(owner)

