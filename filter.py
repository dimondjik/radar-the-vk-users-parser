import sqlite3
from datetime import datetime
from math import ceil

# Users with no city are cut off


def clear_tables():
    with sqlite3.connect('db/users_filtered.db') as db:
        cursor = db.cursor()
        cursor.execute('DELETE FROM users')
        # cursor.execute('DELETE FROM users_no_city')


sql_insert_users = 'INSERT INTO ' \
                   'users(id, first_name, last_name, age) ' \
                   'VALUES(?,?,?,?)'

# sql_insert_users_no_city = 'INSERT INTO ' \
#                            'users_no_city(id, first_name, last_name, sex, \
#                            relation, is_closed, bdate, country, city) ' \
#                            'VALUES(?,?,?,?,?,?,?,?,?)'


# def filter_users(city=True):
def filter_users():
    # Relation
    # 0 - None
    # 1 - Single
    # 8 - Actively searching (?)

    # Use find_city_id to identify country and city
    # City, country
    # 1 - Moscow
    # 1 - Russia

    def filter_user(item):

        item = list(item)

        city_id = '1'
        country_id = '1'
        # From - to
        age = (17, 25)
        relations = ('0', '1', '8')

        if not (item[4] in relations):
            return False, None

        if len(item[6].split('.')) < 3:
            return False, None
        else:
            try:
                user_age = round((datetime.now() - datetime.strptime(item[6], '%d.%m.%Y')).days / 365, 1)
                if not (age[0] <= user_age <= age[1]):
                    return False, None
                else:
                    item[6] = user_age
            except ValueError as e:
                # Caught 31 of February, Vk is a mess
                if 'day is out of range for month' in str(e):
                    return False, None
                else:
                    raise

        # if city:
        if item[8] != city_id:
            return False, None

        return True, item

    with sqlite3.connect('db/users_sorted.db') as db:
        cursor = db.cursor()
        # if city:
        cursor.execute('SELECT * FROM users')
        # else:
        #     cursor.execute('SELECT * FROM users_no_city')
        users = cursor.fetchall()

    with sqlite3.connect('db/users_filtered.db') as db:
        cursor = db.cursor()
        for user in users:
            data = filter_user(user)
            if data[0]:
                # if city:
                cursor.execute(sql_insert_users, (data[1][0], data[1][1], data[1][2], data[1][6]))
                # else:
                #     cursor.execute(sql_insert_users_no_city, user)


clear_tables()

# Users with city specified are more adequate
filter_users()
# filter_users(city=True)
# filter_users(city=False)
