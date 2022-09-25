import sqlite3

with sqlite3.connect('users_precise.db') as db:
    cursor = db.cursor()
    sql = 'SELECT * FROM users'
    cursor.execute(sql)
    data = cursor.fetchall()

with sqlite3.connect('users_display.db') as db:
    cursor = db.cursor()
    sql = 'INSERT INTO users(id, first_name, last_name, age, groups, video, ' \
          'audio, match, match_groups, viewed, bookmarked) ' \
          'VALUES(?,?,?,?,?,?,?,?,?,?,?)'
    for user in data:
        user = list(user)
        user += ['0', '0']
        cursor.execute(sql, user)
