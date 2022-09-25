import vk_api
import sqlite3
import json
import configparser

cfg = configparser.ConfigParser()
cfg.read('./config/config.cfg')
accounts = json.loads(cfg['ACCOUNTS']['bots'])

vk_client = vk_api.VkApi(
    token=list(accounts[0].values())[0])
client = vk_client.get_api()

# TODO: CHANGE TO YOUR VK ID
# ----------------------------------------------------------------------------------------------------------------------
from_user = cfg['TARGET']['target_id']
# ----------------------------------------------------------------------------------------------------------------------

targets = client.groups.get(user_id=from_user, extended=1)

sql = 'INSERT INTO targets(id, name, processed) VALUES(?,?,?)'

print('Found {0} groups from {1}'.format(targets['count'], from_user))
print('Writing into targets')
for target in targets['items']:
    with sqlite3.connect('db/users_raw.db') as db:
        db_cursor = db.cursor()
        try:
            db_cursor.execute(sql, (target['id'], target['name'], 'no'))
        except sqlite3.IntegrityError:
            continue

print('Done')
