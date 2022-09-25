import vk_api
import asyncio
import random
import aiosqlite
import json
import traceback
import configparser

cfg = configparser.ConfigParser()
cfg.read('./config/config.cfg')
accounts = json.loads(cfg['ACCOUNTS']['bots'])
bots = []
for account in accounts:
    bots.append({'bot': vk_api.VkApi(token=list(account.values())[0]).get_api(),
                 'name': list(account.keys())[0], 'busy': False, 'broken': False})


async def write_to_db(user_id, data, data_type):
    async with aiosqlite.connect('db/users_add_data.db') as db:
        cursor = await db.cursor()
        data = json.dumps(data)
        sql = 'UPDATE users SET {0} = ? WHERE id = ?'.format(data_type)
        await cursor.execute(sql, (data, user_id))
        await db.commit()


async def get_target(data_type):
    async with aiosqlite.connect('db/users_add_data.db') as db:
        cursor = await db.cursor()
        sql = 'SELECT * FROM users WHERE {0} IS NULL'.format(data_type)
        await cursor.execute(sql)
        try:
            return (await cursor.fetchone())[0]
        except TypeError:
            return 0


async def delete_from_db(user_id):
    async with aiosqlite.connect('db/users_add_data.db') as db:
        cursor = await db.cursor()
        sql = 'DELETE FROM users WHERE id = ?'
        await cursor.execute(sql, (user_id, ))
        await db.commit()


def get_free_bot():
    not_broken_bots = []
    free_bots = []

    for bot in bots:
        if not bot['broken']:
            not_broken_bots.append(bot)

    for bot in not_broken_bots:
        if not bot['busy']:
            free_bots.append(bot)

    if free_bots:
        return random.choice(free_bots)
    elif not_broken_bots:
        return 'busy'
    else:
        return 'broken'


def get_client_from_bot(bot):
    return bot['bot']


def set_bot_busy(bot, busy: bool):
    bot['busy'] = busy


def set_bot_broken(bot, broken: bool):
    bot['broken'] = broken


async def get_groups():
    while True:
        target = int(await get_target('groups'))
        if target:
            try:
                working_bot = get_free_bot()
                while working_bot == 'busy':
                    working_bot = get_free_bot()
                if working_bot == 'broken':
                    print('Every bot is broken')
                    break
                set_bot_busy(working_bot, True)
                print('Working with: {}'.format(working_bot['name']))

                groups = get_client_from_bot(working_bot).groups.get(user_id=target, count=1000, extended=1)
                print('Получили группы ({0}) от {1}'.format(groups['count'], target))

                group_list = []
                for group in groups['items']:
                    group_list.append([group['id'], group['name']])

                set_bot_busy(working_bot, False)
                await write_to_db(target, group_list, 'groups')
                print('Успешно записали в базу группы от {0}'.format(target))
            except vk_api.exceptions.ApiError as e:
                if '[201] Access denied' in str(e):
                    print('Группы {0} скрыты?\n{1}'.format(target, e))
                    set_bot_busy(working_bot, False)
                    await write_to_db(target, [], 'groups')
                    print('Успешно записали в базу группы от {0}'.format(target))
                elif '[30] This profile is private' in str(e):
                    print('Пользователь {0} стал приватным пока мы всё обрабатывали\n{1}'.format(target, e))
                    set_bot_busy(working_bot, False)
                    await delete_from_db(target)
                    print('Удалили пользователя {0}'.format(target))
                elif ('[18] User was deleted or banned' in str(e)) or \
                        ('[15] Access denied: user deactivated' in str(e)):
                    print('Пользователя {0} забанили пока мы всё обрабатывали 0_0\n{1}'.format(target, e))
                    set_bot_busy(working_bot, False)
                    await delete_from_db(target)
                    print('Удалили пользователя {0}'.format(target))
                elif '[15] Access denied: owner blocked' in str(e):
                    print('Группы {0} скрыты?\n{1}'.format(target, e))
                    set_bot_busy(working_bot, False)
                    await write_to_db(target, [], 'groups')
                    print('Успешно записали в базу группы от {0}'.format(target))
                elif '[29] Rate limit reached' in str(e):
                    print('Группы всё, ударились в лимит\n{0}'.format(e))
                    set_bot_broken(working_bot, True)
                    set_bot_busy(working_bot, False)
                    continue
                elif '[10] Internal server error: could not check access_token now, check later' in str(e):
                    print('Внутренняя ошибка вк, ждём...\n{0}'.format(e))
                    set_bot_busy(working_bot, False)
                    await asyncio.sleep(5)
                else:
                    print(traceback.format_exc())
                    set_bot_broken(working_bot, True)
                    set_bot_busy(working_bot, False)
                    break
            except vk_api.exceptions.Captcha as captcha:
                set_bot_busy(working_bot, False)
                print(captcha.get_url())
                captcha.try_again(input('Словили капчу, введи решение: '))
                continue
            except:
                set_bot_broken(working_bot, True)
                set_bot_busy(working_bot, False)
                print(traceback.format_exc())
                break
            await asyncio.sleep(random.randint(1, 2))
        else:
            set_bot_busy(working_bot, False)
            print('Получили группы всех пользователей!')
            break


'''async def get_audio():
    while True:
        target = int(await get_target('audio'))
        if target:
            try:
                working_bot = get_free_bot()
                while working_bot == 'busy':
                    working_bot = get_free_bot()
                if working_bot == 'broken':
                    print('Every bot is broken')
                    break
                set_bot_busy(working_bot, True)
                print('Working with: {}'.format(working_bot['name']))

                audios = get_client_from_bot(working_bot).audio.get(owner_id=target, count=100)
                print('Получили аудио ({0}) от {1}'.format(audios['count'], target))

                audio_list = []
                for audio in audios['items']:
                    audio_list.append([audio['artist'], audio['title']])

                set_bot_busy(working_bot, False)
                await write_to_db(target, audio_list, 'audio')
                print('Успешно записали в базу аудио от {0}'.format(target))
            except vk_api.exceptions.ApiError as e:
                if '[201] Access denied' in str(e):
                    print('Аудио {0} скрыты?\n{1}'.format(target, e))
                    set_bot_busy(working_bot, False)
                    await write_to_db(target, [], 'audio')
                    print('Успешно записали в базу аудио от {0}'.format(target))
                elif '[30] This profile is private' in str(e):
                    print('Пользователь {0} стал приватным пока мы всё обрабатывали\n{1}'.format(target, e))
                    set_bot_busy(working_bot, False)
                    await delete_from_db(target)
                    print('Удалили пользователя {0}'.format(target))
                elif ('[18] User was deleted or banned' in str(e)) or \
                        ('[15] Access denied: user deactivated' in str(e)):
                    print('Пользователя {0} забанили пока мы всё обрабатывали 0_0\n{1}'.format(target, e))
                    set_bot_busy(working_bot, False)
                    await delete_from_db(target)
                    print('Удалили пользователя {0}'.format(target))
                elif '[15] Access denied: owner blocked' in str(e):
                    print('Аудио {0} скрыты?\n{1}'.format(target, e))
                    set_bot_busy(working_bot, False)
                    await write_to_db(target, [], 'audio')
                    print('Успешно записали в базу аудио от {0}'.format(target))
                elif '[29] Rate limit reached' in str(e):
                    print('Аудио всё, ударились в лимит\n{0}'.format(e))
                    set_bot_broken(working_bot, True)
                    set_bot_busy(working_bot, False)
                    continue
                elif '[10] Internal server error: could not check access_token now, check later' in str(e):
                    print('Внутренняя ошибка вк, ждём...\n{0}'.format(e))
                    set_bot_busy(working_bot, False)
                    await asyncio.sleep(5)
                else:
                    set_bot_broken(working_bot, True)
                    set_bot_busy(working_bot, False)
                    print(traceback.format_exc())
                    break
            except vk_api.exceptions.Captcha as captcha:
                set_bot_busy(working_bot, False)
                print(captcha.get_url())
                captcha.try_again(input('Словили капчу, введи решение: '))
                continue
            except:
                set_bot_broken(working_bot, True)
                set_bot_busy(working_bot, False)
                print(traceback.format_exc())
                break

            await asyncio.sleep(random.randint(1, 2))
        else:
            print('Получили аудио всех пользователей!')
            break'''


async def get_audio():
    while True:
        target = int(await get_target('audio'))
        if target:
            await write_to_db(target, [], 'audio')
        else:
            print('Проставили везде в аудио пробелы (извините, исправления в процессе)')
            break


async def get_video():
    while True:
        target = int(await get_target('video'))
        if target:
            try:
                working_bot = get_free_bot()
                while working_bot == 'busy':
                    working_bot = get_free_bot()
                if working_bot == 'broken':
                    print('Every bot is broken')
                    break
                set_bot_busy(working_bot, True)
                print('Working with: {}'.format(working_bot['name']))

                videos = get_client_from_bot(working_bot).video.get(owner_id=target, count=10)
                print('Получили видео ({0}) от {1}'.format(videos['count'], target))

                video_list = []
                for video in videos['items']:
                    if not('content_restricted' in video.keys()):
                        try:
                            video_list.append([video['title'], video['player']])
                        except KeyError:
                            pass

                set_bot_busy(working_bot, False)
                await write_to_db(target, video_list, 'video')
                print('Успешно записали в базу видео от {0}'.format(target))
            except vk_api.exceptions.ApiError as e:
                if '[201] Access denied' in str(e):
                    print('Видео {0} скрыты?\n{1}'.format(target, e))
                    set_bot_busy(working_bot, False)
                    await write_to_db(target, [], 'video')
                    print('Успешно записали в базу видео от {0}'.format(target))
                elif '[30] This profile is private' in str(e):
                    print('Пользователь {0} стал приватным пока мы всё обрабатывали\n{1}'.format(target, e))
                    set_bot_busy(working_bot, False)
                    await delete_from_db(target)
                    print('Удалили пользователя {0}'.format(target))
                elif ('[18] User was deleted or banned' in str(e)) or \
                        ('[15] Access denied: user deactivated' in str(e)):
                    print('Пользователя {0} забанили пока мы всё обрабатывали 0_0\n{1}'.format(target, e))
                    set_bot_busy(working_bot, False)
                    await delete_from_db(target)
                    print('Удалили пользователя {0}'.format(target))
                elif '[15] Access denied: owner blocked' in str(e):
                    print('Видео {0} скрыты?\n{1}'.format(target, e))
                    set_bot_busy(working_bot, False)
                    await write_to_db(target, [], 'video')
                    print('Успешно записали в базу видео от {0}'.format(target))
                elif '[29] Rate limit reached' in str(e):
                    print('Видео всё, ударились в лимит\n{0}'.format(e))
                    set_bot_broken(working_bot, True)
                    set_bot_busy(working_bot, False)
                    continue
                elif '[10] Internal server error: could not check access_token now, check later' in str(e):
                    print('Внутренняя ошибка вк, ждём...\n{0}'.format(e))
                    set_bot_busy(working_bot, False)
                    await asyncio.sleep(5)
                else:
                    set_bot_broken(working_bot, True)
                    set_bot_busy(working_bot, False)
                    print(traceback.format_exc())
                    break
            except vk_api.exceptions.Captcha as captcha:
                print(captcha.get_url())
                set_bot_busy(working_bot, False)
                captcha.try_again(input('Словили капчу, введи решение: '))
                continue
            except:
                set_bot_broken(working_bot, True)
                set_bot_busy(working_bot, False)
                print(traceback.format_exc())
                break
            await asyncio.sleep(random.randint(1, 2))
        else:
            print('Получили видео всех пользователей!')
            break


mainloop = asyncio.get_event_loop()
tasks = [
    mainloop.create_task(get_audio()),
    mainloop.create_task(get_video()),
    mainloop.create_task(get_groups())
]
mainloop.run_until_complete(asyncio.wait(tasks))
