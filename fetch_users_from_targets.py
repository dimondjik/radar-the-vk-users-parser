import vk_api
import sqlite3
from time import sleep as delay
import configparser
import json

cfg = configparser.ConfigParser()
cfg.read('./config/config.cfg')
accounts = json.loads(cfg['ACCOUNTS']['bots'])
clients = []
for account in accounts:
    clients.append(vk_api.VkApi(token=list(account.values())[0]).get_api())

client_idx = 0

client = clients[client_idx]


# Documentation suggests that max is 25 API calls, but 25 gives HTTP 500, 10 for now
# It fetches 10k users per call
def vkscript_for_getmembers(group_id, offset):
    return 'var api_call_counter = 10;\n' \
           'var current_offset = %i;\n' \
           'var members = [];\n' \
           'while (api_call_counter != 0) {\n' \
           'members = members + ' \
           'API.groups.getMembers({"group_id": %i, "offset": current_offset, "count": 1000, ' \
           '"fields": "sex, country, city, bdate, relation"}).items;\n' \
           'current_offset = current_offset + 1000;\n' \
           'api_call_counter = api_call_counter - 1;\n' \
           '}\n' \
           'return {"members": members, "current_offset": current_offset};\n' % (offset, int(group_id))


def get_available_target():
    with sqlite3.connect('db/users_raw.db') as db:
        db_cursor = db.cursor()
        sql = 'SELECT * FROM targets WHERE processed = "no"'
        db_cursor.execute(sql)
        data = db_cursor.fetchall()
        if data:
            return data[0]
        else:
            return ()


def mark_target_as_done(group):
    with sqlite3.connect('db/users_raw.db') as db:
        db_cursor = db.cursor()
        sql = 'UPDATE targets SET processed = "yes" WHERE id = ?'
        db_cursor.execute(sql, (group[0],))


def get_offset(group):
    with sqlite3.connect('db/users_raw.db') as db:
        cursor = db.cursor()
        sql = 'SELECT * FROM targets WHERE id = ?'
        cursor.execute(sql, (group[0],))
        data = cursor.fetchall()
        try:
            return int(data[0][3])
        except TypeError:
            return 0


def update_offset(group, offset):
    offset = str(offset)
    with sqlite3.connect('db/users_raw.db') as db:
        cursor = db.cursor()
        sql = 'UPDATE targets SET current_offset = ? WHERE id = ?'
        cursor.execute(sql, (offset, group[0]))


def delete_group_from_targets(group):
    with sqlite3.connect('db/users_raw.db') as db:
        db_cursor = db.cursor()
        sql = 'DELETE FROM targets WHERE id = ?'
        db_cursor.execute(sql, (group[0],))


def write_members_to_db(users):
    with sqlite3.connect('db/users_raw.db') as db:
        db_cursor = db.cursor()

        sql = 'INSERT INTO users(id, first_name, last_name, sex, relation, is_closed, bdate, country, city) ' \
              'VALUES(?,?,?,?,?,?,?,?,?)'

        banned_users_count = 0

        already_in_db_users_count = 0

        for user in users:
            try:
                fields = user.keys()
            except AttributeError:
                return False
            if 'deactivated' in fields:
                # Banned user
                # print('Caught banned user')
                banned_users_count += 1
                pass
            else:
                idx = user['id']
                first_name = user['first_name']
                last_name = user['last_name']
                is_closed = user['is_closed']

                sex = None
                relation = None
                bdate = None
                country = None
                city = None

                if 'relation' in fields:
                    relation = user['relation']
                if 'sex' in fields:
                    sex = user['sex']
                if 'bdate' in fields:
                    bdate = user['bdate']
                if 'city' in fields:
                    city = user['city']['id']
                if 'country' in fields:
                    country = user['country']['id']

                try:
                    db_cursor.execute(sql, (idx, first_name, last_name, sex, relation,
                                            is_closed, bdate, country, city))
                except sqlite3.IntegrityError:
                    # Id is not unique
                    already_in_db_users_count += 1

    print('Caught {0} banned users'.format(banned_users_count))
    print('{0} users already in db'.format(already_in_db_users_count))
    return True


def fetch_members(group):
    group_id = group[0]

    try:
        group_total_members = int(client.groups.getMembers(group_id=group_id, count=0)['count'])
    except vk_api.exceptions.ApiError as e:
        return False, e

    current_offset = get_offset(group)

    fetched_total_members = get_offset(group)

    print('Fetching from {0}...'.format(group[1]))
    while current_offset < group_total_members:
        try:
            data = client.execute(code=vkscript_for_getmembers(group_id, current_offset))

            fetched_total_members += len(data['members'])
            print('Fetched {0} users out of {1} ({2}%)'.format(fetched_total_members, group_total_members,
                                                               round(fetched_total_members /
                                                                     group_total_members * 100)))
        except vk_api.exceptions.ApiHttpError:
            print('Vk broke our request (Internal Server Error), waiting 10 sec...')
            delay(10)
            print('Retrying...')
            continue
        except vk_api.exceptions.ApiError as e:
            return False, e

        print('Adding {0} users to db'.format(len(data['members'])))

        if not write_members_to_db(data['members']):
            return False, '[29] Rate limit reached'
        print('Done adding')

        current_offset = int(data['current_offset'])

        update_offset(group, current_offset)

        delay(1)
    print('Done fetching')

    return True, None


def fetch_from_targets():
    global client, clients, client_idx

    while True:
        group = get_available_target()
        if group:
            print('Using client {0}'.format(client_idx))
            data = fetch_members(group)
            if data[0]:
                mark_target_as_done(group)
                update_offset(group, -1)
            else:
                if '[29] Rate limit reached' in str(data[1]):
                    print('Client {0} caught rate limit'.format(client_idx))
                    client_idx += 1
                    if (client_idx + 1) > len(clients):
                        print('No clients left, the only option is to wait')
                        break
                    else:
                        print('Switching to client {0}'.format(client_idx))
                        client = clients[client_idx]
                        continue
                else:
                    print('Something went wrong while processing "{0}" ({1})\n'
                          '{2}'.format(group[1], group[0], data[1]))
                    if input('Delete this group from targets? [y/n]: ') == 'y':
                        delete_group_from_targets(group)
                        if input('Continue? [y/n]: ') == 'y':
                            continue
                        else:
                            break
                    else:
                        break
        else:
            print('No targets left, all done')
            break


fetch_from_targets()
