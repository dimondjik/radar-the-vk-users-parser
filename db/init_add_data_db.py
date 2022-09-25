import sqlite3

with sqlite3.connect('users_add_data.db') as db:
    sql_1 = '''CREATE TABLE "users" 
    (
    "id"    TEXT UNIQUE,
    "first_name"	TEXT,
    "last_name"  TEXT,
    "age" TEXT,
    "groups" TEXT,
    "video" TEXT,
    "audio" TEXT,
    PRIMARY KEY("id")
    );'''

    cursor = db.cursor()
    cursor.execute(sql_1)
