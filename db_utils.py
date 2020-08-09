import sqlite3
from roles import roles
from config import database_name
from shelves_utils import get_players
from shelves_utils import delete_info
from random import shuffle


def work_with_db(func, *params):
    """Вся работа с бд реализуется через эту ф-цию"""
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    with conn:
        result = func(cursor, *params)
    conn.commit()
    conn.close()
    return result


def start(cursor: sqlite3.Cursor, chat_id: int):
    """Команда бота start в групее"""
    # Добавляем чат в бд
    sql = """INSERT INTO Chats
    VALUES(?,?);"""
    cursor.execute(sql, (chat_id, 'Registration'))


def user_in_game(cursor: sqlite3.Cursor, player_id: int):
    """Проверка нахождения пользователся в игре"""
    sql = """SELECT Id
    FROM Players
    WHERE Id=(?);"""
    result = cursor.execute(sql, (player_id,)).fetchall()
    return result != []


def chat_in_game(cursor: sqlite3.Cursor, chat_id):
    """Проверка нахождения чата в игре"""
    sql = """SELECT Id
        FROM Chats
        WHERE Id=(?);"""
    result = cursor.execute(sql, (chat_id,)).fetchall()
    return result != []


def check_chat_status(cursor: sqlite3.Cursor, chat_id: int, params: list):
    """Проверка статуса чата"""
    sql = """SELECT Status
    FROM Chats
    WHERE id = (?);"""
    result = cursor.execute(sql, (chat_id,)).fetchall()
    return result[0][0] in params


def set_chat_status(cursor: sqlite3.Cursor, chat_id: int, status: str):
    """Установка статуса чата"""
    sql = """UPDATE Chats
    SET Status = (?)
    WHERE Id=(?);"""
    cursor.execute(sql, (status, chat_id))


def reg_users(cursor: sqlite3.Cursor, chat_id: int):
    """Регистарция игроков в бд"""
    # Тут будет сложно
    # Получаем список игроков
    players = get_players(chat_id)
    # Получаем роли
    role_list = roles[str(len(players))]
    shuffle(role_list)

    sql = """INSERT INTO Players
    VALUES (?,?,?,?,?,?,?,?,?);"""
    delete_info(chat_id)
    for player, role in zip(players, role_list):
        cursor.execute(sql, (player[0], player[1], player[2], chat_id, role, 'Registered', 1, 0, 0))


def delete_chat(cursor: sqlite3.Cursor, chat_id: int):
    """Удадение чата из бд"""
    # Сначала удаляем игроков
    sql = """DELETE FROM Players
    WHERE Chat = (?);"""
    cursor.execute(sql, (chat_id,))
    # Потом удаляем чат
    sql = """DELETE FROM Chats
        WHERE Id = (?);"""
    cursor.execute(sql, (chat_id,))


def get_players_info(cursor: sqlite3.Cursor, player_id: int):
    """Получение информации """
    sql = """SELECT *
    FROM Players
    WHERE Id = (?);"""

    result = cursor.execute(sql, (player_id,)).fetchall()
    return result[0]


def change_players_info(cursor: sqlite3.Cursor, player_id: int, key: str, value):
    """Смена статуса у игрока"""
    sql = """UPDATE Players
    SET (?)=(?),
    WHERE Id=(?);"""

    cursor.execute(sql, (key, value, player_id))
