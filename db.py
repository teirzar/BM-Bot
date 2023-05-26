import sqlite3


class DBconnect:
    def __init__(self, name_table: str, src: str):
        self.__name_table = name_table
        self.__src = src
        with sqlite3.connect(self.__src) as db:
            c = db.cursor()
            c.execute(f"""CREATE TABLE IF NOT EXISTS {self.__name_table} (id integer);  """)
            c.execute(f"""PRAGMA table_info("{self.__name_table}"); """)
            column_names = [i[1] for i in c.fetchall()]
        self.__columns = column_names

    def __str__(self):
        return self.__name_table

    def __len__(self):
        return len(self.print_table())

    def names(self):
        return self.__columns

    def __check_args(self, args) -> bool:
        for el in args:
            if el not in self.__columns:
                if "(" in el and ")" in el:
                    if el.split(")")[0].split("(")[1] not in self.__columns:
                        print(f'Функция [{el.split("(")[0]}] '
                              f'содержит недопустимую колонку [{el.split(")")[0].split("(")[1]}]')
                        return True
                else:
                    print("Столбец [" + el + "] отсутствует в таблице")
                    return True

    def append_column(self, name: str, column_definition: str='') -> None:
        if name in self.__columns:
            return
        self.__columns.append(name)
        with sqlite3.connect(self.__src) as db:
            c = db.cursor()
            c.execute(f"""ALTER TABLE {self.__name_table} ADD {name} {column_definition};""")
        print(f"Столбец [{name}] добавлен в таблицу [{self.__name_table}]")

    def print_table(self, *args, where='', order_by='', group_by='', add='') -> list[tuple]:
        if self.__check_args(args):
            return []
        with sqlite3.connect(self.__src) as db:
            c = db.cursor()
            c.execute(f"""SELECT {', '.join(el for el in args) if args else '*'} FROM {self.__name_table} 
                        {"WHERE " + where if where else ""}
                        {"ORDER BY " + order_by if order_by else ""}
                        {"GROUP BY " + group_by if group_by else ""}
                        {add}""")
            res = c.fetchall()
        return res

    def sql_executescript(self, text: str) -> list:
        with sqlite3.connect(self.__src) as db:
            c = db.cursor()
            c.executescript(f"""{text}""")
            res = c.fetchall()
        return res

    def write(self, *args, values='') -> None:
        if args:
            if self.__check_args(args):
                return
        with sqlite3.connect(self.__src) as db:
            c = db.cursor()
            c.execute(f"INSERT INTO {self.__name_table} {'(' + ', '.join(el for el in args) + ')' if args else ''} "
                      f"VALUES ({values});")
        print(f"Значения [{values}] записаны в столбцы [{args}]")

    def delete(self, where='') -> None:
        with sqlite3.connect(self.__src) as db:
            c = db.cursor()
            c.execute(f'DELETE FROM {self.__name_table} {"WHERE " + where if where else ""}')
        print(f"Из таблицы [{self.__name_table}] удалено [{where}]")

    def update(self, dbset='', where=''):
        with sqlite3.connect(self.__src) as db:
            c = db.cursor()
            c.execute(f'UPDATE {self.__name_table} SET {dbset} {"WHERE " + where if where else ""}')
        if self.__name_table not in ("position", "cposition", "admbuilder", "orders"):
            print(f"В талицу [{self.__name_table}] присвоены значения [{dbset}] где [{where}]")
