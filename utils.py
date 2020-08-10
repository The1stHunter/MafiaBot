import sqlite3
from random import shuffle
from config import database_name
from config import shelve_name
import roles
import shelve
import os
from telebot import types
from game import Game
from player import Player


def add_row(player_id: str, chat_id: str, name: str, surname: str):
    """Добавление информации о новом игроке"""
    sql = """INSERT INTO Players (id, chat, name, surname, role_status)
    VALUES (?, ?, ?, ?, ?);"""

    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    cursor.execute(sql, (player_id, chat_id, name, surname, '1'))
    conn.commit()
    conn.close()


def delete_chat(chat_id: str):
    """Удаление информации о всех участниках чата"""
    sql = """DELETE FROM Players
    WHERE chat = (?);"""

    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    cursor.execute(sql, (chat_id,))
    conn.commit()
    conn.close()


def check_player(player_id):
    """Проверка, является ли пользователь участником какой-то игры"""
    sql = """SELECT *
    FROM Players
    WHERE id = (?);"""

    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    result = cursor.execute(sql, (player_id,)).fetchall()
    conn.close()
    return True if result else False


def get_chat(player_id: str):
    """Возвращает чат в котором играет пользователь"""
    sql = """SELECT chat
    FROM Players
    WHERE id = (?);"""

    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    result = cursor.execute(sql, (player_id,)).fetchall()
    conn.close()
    return result[0][0] if result else result


def count_players(chat_id: str):
    """Возвращает количество игроков в чате"""
    sql = """SELECT COUNT(id)
    FROM Players
    WHERE chat = (?);"""

    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    result = cursor.execute(sql, (chat_id,)).fetchall()
    conn.close()
    return int(result[0][0]) if result else result


def get_players(chat_id: str):
    """Возвращает игроков в чате"""
    sql = """SELECT id
    FROM Players
    WHERE chat = (?);"""

    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    result = [x[0] for x in cursor.execute(sql, (chat_id,)).fetchall()]
    conn.close()
    return result


def get_players_info(chat_id: str):
    """Возвращает информацию об игроках в чате"""
    """Возвращает игроков в чате"""
    sql = """SELECT id, name, surname
    FROM Players
    WHERE chat = (?);"""

    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    result = cursor.execute(sql, (chat_id,)).fetchall()
    conn.close()
    return result


def change_role_status(player_id: str, role_status: str):
    """Меняет статус получения роли игрока"""
    sql = """UPDATE Players
    SET role_status=(?)
    WHERE id=(?);"""

    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    cursor.execute(sql, (role_status, player_id))
    conn.commit()
    conn.close()


def get_role_status(player_id: str):
    sql = """SELECT role_status
    FROM Players
    WHERE id = (?);"""

    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    result = cursor.execute(sql, (player_id,)).fetchall()
    conn.close()
    return result[0][0] if result else result


def start_game(chat_id: str, players_info: list):
    """Создание новой игры"""
    assert roles.minimum <= len(players_info) <= roles.maximum, 'Incorrect count of players'
    game = Game(int(chat_id))
    for player in players_info:
        pl = Player(int(player[0]), player[1], player[2])
        game.add_player(pl)
    msg = game.next_condition()
    with shelve.open(shelve_name) as storage:
        storage[str(chat_id)] = game
    return msg


def get_game(chat_id: int):
    """Получение информации о данной игре"""
    with shelve.open(shelve_name) as storage:
        return storage[str(chat_id)]


def set_game(chat_id: int, game: Game):
    """Установка обновлений в игре"""
    with shelve.open(shelve_name) as storage:
        storage[str(chat_id)] = game


def end_game(chat_id: str):
    """Удаление информации об игре"""
    with shelve.open(shelve_name) as game:
        try:
            del game[str(chat_id)]
        except KeyError:
            pass


