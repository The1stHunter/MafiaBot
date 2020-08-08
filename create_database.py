from config import database_name
import sqlite3


# Создание таблицы ролей
sql_roles = """CREATE TABLE Roles(
Name TEXT PRIMARY KEY,
Color TEXT NOT NULL,
CONSTRAINT check_color CHECK (Color in ('Black', 'Red')));"""

# Создание таблицы чатов
sql_chats = """CREATE TABLE Chats(
Id INTEGER PRIMARY KEY,
Status TEXT NOT NULL,
CONSTRAINT check_status CHECK (Status in ('NotInGame', 'Discussion', 'Vote', 'Mafia', 'Sheriff')));"""

# Создание таблицы игроков
sql_players = """CREATE TABLE Players(
Id INTEGER PRIMARY KEY,
Name TEXT,
Surname TEXT,
Chat INTEGER,
Role TEXT,
Game_status TEXT,
Stand_in_vote_status INTEGER,
Vote_status INTEGER,
CONSTRAINT check_game_status CHECK (Game_status in ('NotInGame', 'Registered', 'GetRole', 'InGame', 'Killed')),
CONSTRAINT check_stand_in_cote_status CHECK (Stand_in_vote_status in (0, 1)),
CONSTRAINT check_vote_status CHECK (Vote_status in (0, 1)),
CONSTRAINT fk_role FOREIGN KEY (Role) REFERENCES Roles (Name),
CONSTRAINT fk_chat FOREIGN KEY (Chat) REFERENCES Chat (Id));"""

# Содержимое таблицы ролей
roles = [('Don', 'Black'), ('Mafia', 'Black'), ('Civilian', 'Red'), ('Sheriff', 'Red')]
sql_insert = 'INSERT INTO Roles VALUES (?, ?)'

if __name__ == '__main__':
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    cursor.execute(sql_roles)
    cursor.execute(sql_chats)
    cursor.execute(sql_players)
    for role in roles:
        cursor.execute(sql_insert, role)
    conn.commit()
    conn.close()
