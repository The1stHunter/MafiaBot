import sqlite3
from config import database_name


sql_database_create = """CREATE TABLE Players(
id TEXT,
chat TEXT,
name TEXT,
surname TEXT,
role_status TEXT,
CONSTRAINT pk PRIMARY KEY (id),
CONSTRAINT check_role_status CHECK (role_status in ('1', '2', '3')));"""


if __name__ == '__main__':
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    cursor.execute(sql_database_create)
    conn.commit()
    conn.close()
