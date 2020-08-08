"""Каждое хранилище имеет ключ Players значением которого является список игроков
Каждый игрок является списком (Идентификатор, Имя, Фамилия)
Данный файл используется для предварительной регистрации пользователей"""

import shelve
from config import shelve_name
import os


def start(chat_id: int):
    """Команда start бота в группе"""
    with shelve.open(shelve_name+f'{chat_id}') as storage:
        storage['players'] = []


def delete_info(chat_id: int):
    """Удаление информации о предварительной регистрации"""
    try:
        os.remove(shelve_name + f'{chat_id}.bak')
        os.remove(shelve_name + f'{chat_id}.dat')
        os.remove(shelve_name + f'{chat_id}.dir')
    except FileNotFoundError:
        pass


def user_in_game(chat_id: int, player_id: int):
    """Проверка является ли пользователь предварительно зарегестрированным"""
    with shelve.open(shelve_name+f'{chat_id}') as storage:
        for player in storage['players']:
            if player[0] == player_id:
                return True
    return False


def register_user(chat_id: int, player_id: int, first_name: str, last_name: str):
    """Предвраительная регистрация пользователей"""
    with shelve.open(shelve_name+f'{chat_id}') as storage:
        storage['players'] += [[player_id, first_name, last_name]]


def players_count(chat_id: int):
    """Количетсво предварительно зарегестрированных пользователей"""
    with shelve.open(shelve_name + f'{chat_id}') as storage:
        return len(storage['players'])


def get_players(chat_id: int):
    """Возвращает данные об игроках"""
    with shelve.open(shelve_name + f'{chat_id}') as storage:
        return storage['players']
