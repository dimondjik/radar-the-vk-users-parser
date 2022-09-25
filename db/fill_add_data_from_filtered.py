import sqlite3

with sqlite3.connect('users_filtered.db') as db:
    cursor = db.cursor()
    sql = 'SELECT * FROM users'
    cursor.execute(sql)
    data = cursor.fetchall()

with sqlite3.connect('users_add_data.db') as db:
    cursor = db.cursor()
    sql = 'INSERT INTO users(id, first_name, last_name, age, groups, video, audio) ' \
          'VALUES(?,?,?,?,?,?,?)'
    for user in data:
        user = list(user)
        user += [None, None, None]
        cursor.execute(sql, user)
