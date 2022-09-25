import sqlite3
import json

with sqlite3.connect('db/users_raw.db') as db:
    cursor = db.cursor()
    sql = 'SELECT * FROM targets'
    cursor.execute(sql)
    data = cursor.fetchall()

targets = []
for target in data:
    targets.append(int(target[0]))

with sqlite3.connect('db/users_add_data.db') as db:
    cursor = db.cursor()
    sql = 'SELECT * FROM users'
    cursor.execute(sql)
    data = cursor.fetchall()


with sqlite3.connect('db/users_precise.db') as db:
    cursor = db.cursor()
    cursor.execute('DELETE FROM users')


precise_data = []
base = len(targets)

preview_groups = 10
preview_music = 20
preview_videos = 5

unsorted_precise = []

for user in data:
    match_counter = 0
    match_groups = []

    groups = json.loads(user[4])

    for target in targets:
        for group in groups:
            if target == group[0]:
                match_counter += 1
                match_groups.append(group)

    # match = round(match_counter / base * 100, 1)

    groups = groups[:preview_groups]
    videos = json.loads(user[5])[:preview_videos]
    music = json.loads(user[6])[:preview_music]

    user_list = list(user)

    user_list[4] = json.dumps(groups)
    user_list[5] = json.dumps(videos)
    user_list[6] = json.dumps(music)
    user_list.append(match_counter)
    user_list.append(json.dumps(match_groups))

    unsorted_precise.append(user_list)


sorted_precise = sorted(unsorted_precise, key=lambda l: l[7], reverse=True)

for user in sorted_precise:
    try:
        with sqlite3.connect('db/users_precise.db') as db:
            cursor = db.cursor()
            sql = 'INSERT INTO users(id, first_name, last_name, age, groups, video, audio, match, match_groups) ' \
                  'VALUES(?,?,?,?,?,?,?,?,?)'
            cursor.execute(sql, user)
    except sqlite3.IntegrityError:
        print('{0} already in db'.format(user[0]))
