import sqlite3

with sqlite3.connect('users_raw.db') as db:
    sql_1 = '''CREATE TABLE "users" 
    (
    "id"    TEXT UNIQUE,
    "first_name"	TEXT,
    "last_name"  TEXT,
    "sex"   TEXT,
    "relation"  TEXT,
    "is_closed"   TEXT,
    "bdate" TEXT,
    "country"   TEXT,
    "city"  TEXT,
    PRIMARY KEY("id")
    );'''

    sql_2 = '''CREATE TABLE "targets" 
        (
        "id"    TEXT UNIQUE,
        "name"	TEXT,
        "processed"  TEXT,
        "current_offset"    TEXT,
        PRIMARY KEY("id")
        );'''

    cursor = db.cursor()
    cursor.execute(sql_1)
    cursor.execute(sql_2)
