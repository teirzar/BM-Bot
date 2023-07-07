from datetime import datetime


# current time
async def get_time() -> str:
    """Возвращает строку времени в формате ГГГГ-ММ-ДД ЧЧ:ММ"""
    return datetime.now().strftime("%Y-%m-%d %H:%M")


# logging
async def add_log(string) -> None:
    """Функция логирования.
    Вносит в txt файл данные в формате 'Время: событие' """
    with open('logs/log.txt', 'a') as log:
        text = f'{await get_time()}: {string}\n'
        log.write(text)
