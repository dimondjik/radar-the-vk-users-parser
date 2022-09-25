import sqlite3

# Users with no city are cut off

with sqlite3.connect('users_sorted.db') as db:
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

    # sql_2 = '''CREATE TABLE "users_no_city"
    # (
    # "id"    TEXT UNIQUE,
    # "first_name"	TEXT,
    # "last_name"  TEXT,
    # "sex"   TEXT,
    # "relation"  TEXT,
    # "is_closed"   TEXT,
    # "bdate" TEXT,
    # "country"   TEXT,
    # "city"  TEXT,
    # PRIMARY KEY("id")
    # );'''

    cursor = db.cursor()
    cursor.execute(sql_1)
    # cursor.execute(sql_2)
