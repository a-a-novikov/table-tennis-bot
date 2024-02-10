# table-tennis-bot
Телеграм-бот для удобной организации игр и проведения турниров по настольному теннису.

<div align="left">
    <a href="https://www.python.org/">
        <img src="https://img.shields.io/badge/python-3.11-yellow"> 
    </a>
    <a href="https://aiogram.dev/">
        <img src="https://img.shields.io/badge/aiogram-3.0b6-blue"> 
    </a>
    <a href="https://www.sqlalchemy.org/">
        <img src="https://img.shields.io/badge/sqlalchemy-2.0.17-red"> 
    </a>
</div>

***

## Разворачивание проекта
1. Создать и активировать виртуальное окружение:
   ```commandline 
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```
2. Установить зависимости:
    ```commandline
    pip install poetry
    poetry install
    ```
3. Создать файл `.env`в корне проекта и заполнить его по примеру с `.example.env`.
4. Прописать путь к каталогу бота для Python:
   ```commandline 
   export PYTHONPATH=$PYTHONPATH:$PWD
   ```
5. Применить миграции БД проекта:

    ```commandline
    alembic upgrade head
    ```
6. Запустить бота:
   ```commandline 
   python src/bot.py
   ```
## FAQ

-----
Q: Ошибка типа `dlopen` в библиотеках **pydantic**/**psycopg2**/**alembic** при работе на компьютере с ARM-процессором:

A: Удалите проблемную библиотеку командой `pip uninstall <имя-библиотеки>`, затем установите ее командой `pip install <имя-библиотеки>`.

----
