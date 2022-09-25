import sqlite3

# Users with no city are cut off

sql_select_users = 'SELECT * FROM users WHERE ' \
                   'is_closed = "0" AND ' \
                   'sex = "1" AND ' \
                   '(bdate IS NOT NULL) AND' \
                   '(country IS NOT NULL) AND ' \
                   '(city IS NOT NULL)'

# sql_select_users_no_city = 'SELECT * FROM users WHERE ' \
#                            'is_closed = "0" AND ' \
#                            'sex = "1" AND ' \
#                            '(bdate IS NOT NULL) AND ' \
#                            '(city IS NULL)'

sql_insert_users = 'INSERT INTO ' \
                   'users(id, first_name, last_name, sex, relation, is_closed, bdate, country, city) ' \
                   'VALUES(?,?,?,?,?,?,?,?,?)'

# sql_insert_users_no_city = 'INSERT INTO ' \
#                            'users_no_city(id, first_name, last_name, sex, \
#                            relation, is_closed, bdate, country, city) ' \
#                            'VALUES(?,?,?,?,?,?,?,?,?)'


def write_users_to_db(users, sql):
    with sqlite3.connect('db/users_sorted.db') as db:
        db_cursor = db.cursor()

        for user in users:
            user_buf = list(user)
            if user_buf[4] is None:
                user_buf[4] = 0
            db_cursor.execute(sql, user_buf)


users_raw = sqlite3.connect('db/users_raw.db')
cursor_raw = users_raw.cursor()

cursor_raw.execute(sql_select_users)
data = cursor_raw.fetchall()
write_users_to_db(data, sql_insert_users)

# cursor_raw.execute(sql_select_users_no_city)
# data = cursor_raw.fetchall()
# write_users_to_db(data, sql_insert_users_no_city)

users_raw.close()
