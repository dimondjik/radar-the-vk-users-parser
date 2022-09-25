import sqlite3

with sqlite3.connect('users_display.db') as db:
    sql_1 = '''CREATE TABLE "users" 
    (
    "id"    TEXT UNIQUE,
    "first_name"	TEXT,
    "last_name"  TEXT,
    "age" TEXT,
    "groups" TEXT,
    "video" TEXT,
    "audio" TEXT,
    "match" TEXT,
    "match_groups" TEXT,
    "viewed" TEXT,
    "bookmarked" TEXT,
    PRIMARY KEY("id")
    );'''

    sql_2 = '''CREATE TABLE "bookmarks" 
        (
        "id"    TEXT UNIQUE,
        "first_name"	TEXT,
        "last_name"  TEXT,
        "age" TEXT,
        "groups" TEXT,
        "video" TEXT,
        "audio" TEXT,
        "match" TEXT,
        "match_groups" TEXT,
        PRIMARY KEY("id")
        );'''

    cursor = db.cursor()
    cursor.execute(sql_1)
    cursor.execute(sql_2)
