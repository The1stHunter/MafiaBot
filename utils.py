"""Здесь будут вспомогательные функции для работы с базой данных"""
import telebot
import sqlite3
from config import database_name


def work_with_db(func, *params):
    """Вся работа с бд реализуется через эту ф-цию"""
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    with conn:
        result = func(cursor, *params)
    conn.close()
    return result

def check_chat_status(cursor: sqlite3.Cursor, chat_id: int, params: list):
    """Проверка статуса чата"""
    sql = """SELECT Status
    FROM Chats
    WHERE id = (?);"""

    result = cursor.execute(sql, (chat_id,)).fetchall()
    return result[0][0] in params


def get_players_info(cursor: sqlite3.Cursor, Id: int):
    sql = """SELECT *
    FROM Players
    WHERE Id = (?);"""

    result = cursor.execute(sql, (Id,)).fetchall()
    return result

def get_players_info_chat(cursor: sqlite3.Cursor, chat_id:int):
    sql = """SELECT *
    FROM Players
    WHERE Chat = (?);"""

    result = cursor.execute(sql, (chat_id,)).fetchall()
    return result
