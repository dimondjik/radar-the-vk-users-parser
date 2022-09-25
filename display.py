import sqlite3
import json
import tkinter as tk
import webbrowser


def get_row_count():
    with sqlite3.connect('db/users_display.db') as db:
        cursor = db.cursor()
        sql = 'SELECT COUNT(*) FROM users'
        cursor.execute(sql)
        return cursor.fetchone()[0]


def get_bookmarks_count():
    with sqlite3.connect('db/users_display.db') as db:
        cursor = db.cursor()
        sql = 'SELECT COUNT(*) FROM bookmarks'
        cursor.execute(sql)
        return cursor.fetchone()[0]


def get_first_unviewed():
    with sqlite3.connect('db/users_display.db') as db:
        cursor = db.cursor()
        sql = 'SELECT rowid, * FROM users WHERE viewed="0"'
        cursor.execute(sql)
        try:
            return cursor.fetchone()[0]
        except TypeError:
            return 0


def set_viewed(row, is_viewed):
    with sqlite3.connect('db/users_display.db') as db:
        cursor = db.cursor()
        sql = 'UPDATE users SET viewed = "{0}" WHERE rowid="{1}"'.format(1 if is_viewed else 0, row)
        cursor.execute(sql)


def get_viewed(row):
    with sqlite3.connect('db/users_display.db') as db:
        cursor = db.cursor()
        sql = 'SELECT * FROM users WHERE rowid="{0}"'.format(row)
        cursor.execute(sql)
        user_buf = cursor.fetchone()
    return True if user_buf[9] == '1' else False


def get_bookmark(user_id):
    with sqlite3.connect('db/users_display.db') as db:
        cursor = db.cursor()
        sql = 'SELECT * FROM users WHERE id="{0}"'.format(user_id)
        cursor.execute(sql)
        user_buf = cursor.fetchone()
    return True if user_buf[10] == '1' else False


def set_bookmark(user_id, is_bookmark):
    with sqlite3.connect('db/users_display.db') as db:
        cursor = db.cursor()
        sql = 'UPDATE users SET bookmarked = "{0}" WHERE id="{1}"'.format(1 if is_bookmark else 0, user_id)
        cursor.execute(sql)


def add_to_bookmarks(user_id):
    set_bookmark(user_id, True)
    with sqlite3.connect('db/users_display.db') as db:
        cursor = db.cursor()
        sql_select = 'SELECT * FROM users WHERE id="{0}"'.format(user_id)
        sql_insert = 'INSERT INTO bookmarks(id, first_name, last_name, age, ' \
                     'groups, video, audio, match, match_groups) VALUES(?,?,?,?,?,?,?,?,?)'
        cursor.execute(sql_select)
        data = cursor.fetchone()[:-2]
        cursor.execute(sql_insert, data)


def remove_from_bookmarks(user_id):
    set_bookmark(user_id, False)
    # TODO: We delete one and reupload full table just to restore rowid
    #  its a mess, need remember not to use rowid for indexing purposes
    with sqlite3.connect('db/users_display.db') as db:
        cursor = db.cursor()
        sql_delete = 'DELETE FROM bookmarks WHERE id="{0}"'.format(user_id)
        cursor.execute(sql_delete)
        sql_select = 'SELECT * FROM bookmarks'
        cursor.execute(sql_select)
        data = cursor.fetchall()
        sql_delete_all = 'DELETE FROM bookmarks'
        cursor.execute(sql_delete_all)
        sql_insert = 'INSERT INTO bookmarks(id, first_name, last_name, age, ' \
                     'groups, video, audio, match, match_groups) VALUES(?,?,?,?,?,?,?,?,?)'
        for piece in data:
            cursor.execute(sql_insert, piece)


row_total = get_row_count()
bookmarks_total = get_bookmarks_count()


def get_user_by_row(rowid):
    global bookmarks_mode
    with sqlite3.connect('db/users_display.db') as db:
        cursor = db.cursor()
        if not bookmarks_mode:
            sql = 'SELECT * FROM users WHERE rowid="{0}"'.format(rowid)
        else:
            sql = 'SELECT * FROM bookmarks WHERE rowid="{0}"'.format(rowid)
        cursor.execute(sql)
        data = cursor.fetchone()

    user_buf = list(data)

    user_buf[0] = int(user_buf[0])

    user_buf[3] = float(user_buf[3])
    user_buf[4] = json.loads(user_buf[4])
    user_buf[5] = json.loads(user_buf[5])
    user_buf[6] = json.loads(user_buf[6])
    user_buf[7] = int(user_buf[7])
    user_buf[8] = json.loads(user_buf[8])

    return user_buf


row_counter = 1


def get_next_row():
    global row_counter, bookmarks_total, bookmarks_mode

    if not bookmarks_mode:
        if (row_counter + 1) > row_total:
            return row_counter
        else:
            row_counter += 1
            return row_counter
    else:
        if (row_counter + 1) > bookmarks_total:
            return row_counter
        else:
            row_counter += 1
            return row_counter


def get_row():
    return row_counter


def get_unviewed_row():
    global row_counter
    row_counter = get_first_unviewed()
    return row_counter


def get_previous_row():
    global row_counter
    if (row_counter - 1) < 1:
        return row_counter
    else:
        row_counter -= 1
        return row_counter


def jump_to_row(row):
    global row_counter
    if row_total < row or 1 > row:
        return row_counter
    else:
        row_counter = row
        return row_counter


root = tk.Tk()

link_label = tk.Label(root, width=20, padx=20, pady=10, fg='blue')
link_label.grid(column=0, row=0)


groups_match_label = tk.Label(root, width=20, padx=20, pady=10)
groups_match_label.grid(column=0, row=1)
groups_match_list = tk.Listbox(root, width=40, height=5, borderwidth=5)
groups_match_list.grid(column=1, row=1)
groups_match_list_scroll = tk.Scrollbar(root)
groups_match_list_scroll.grid(column=2, row=1, ipady=20)
groups_match_list_scroll.config(command=groups_match_list.yview)
groups_match_list.config(yscrollcommand=groups_match_list_scroll.set)

groups_label = tk.Label(root, text='Топ ~10 групп', width=20, padx=20, pady=10)
groups_label.grid(column=0, row=2)
groups_list = tk.Listbox(root, width=40, height=5, borderwidth=5)
groups_list.grid(column=1, row=2)
groups_list_scroll = tk.Scrollbar(root)
groups_list_scroll.grid(column=2, row=2, ipady=20)
groups_list_scroll.config(command=groups_list.yview)
groups_list.config(yscrollcommand=groups_list_scroll.set)

music_label = tk.Label(root, text='Топ ~20 песен', width=20, padx=20, pady=10)
music_label.grid(column=0, row=3)
music_list = tk.Listbox(root, width=40, height=5, borderwidth=5)
music_list.grid(column=1, row=3)
music_list_scroll = tk.Scrollbar(root)
music_list_scroll.grid(column=2, row=3, ipady=20)
music_list_scroll.config(command=music_list.yview)
music_list.config(yscrollcommand=music_list_scroll.set)

videos_label = tk.Label(root, text='Топ ~5 видео', width=20, padx=20, pady=10)
videos_label.grid(column=0, row=4)
videos_list = tk.Listbox(root, width=40, height=5, borderwidth=5)
videos_list.grid(column=1, row=4)
videos_list_scroll = tk.Scrollbar(root)
videos_list_scroll.grid(column=2, row=4, ipady=20)
videos_list_scroll.config(command=videos_list.yview)
videos_list.config(yscrollcommand=videos_list_scroll.set)

navigation_frame = tk.Frame(root)
navigation_frame.grid(column=1, row=0)

bookmarks_frame = tk.Frame(root)
bookmarks_frame.grid(column=1, row=5)


def button_previous_command():
    get_previous_row()
    update_window()


def button_next_command():
    get_next_row()
    update_window()


def button_jump_command():
    get_unviewed_row()
    update_window()


def jump_to_row_entry_command():
    try:
        jump_to_row(int(jump_to_row_entry.get()))
    except ValueError:
        pass
    update_window()


def button_bookmark_command():
    global user, bookmarks_mode, bookmarks_total, row_counter

    if get_bookmark(user[0]):
        remove_from_bookmarks(user[0])
        bookmarks_total = get_bookmarks_count()
        if bookmarks_total == 0:
            bookmarks_mode = False
        if bookmarks_mode:
            if row_counter > 1:
                row_counter -= 1
        update_window()
    else:
        add_to_bookmarks(user[0])
        bookmarks_total = get_bookmarks_count()
        update_window()


def button_bookmarks_mode_command():
    global bookmarks_mode, bookmarks_total, row_counter
    bookmarks_total = get_bookmarks_count()

    if not bookmarks_total == 0:
        bookmarks_mode = not bookmarks_mode
        row_counter = 1
        update_window()


button_bookmark = tk.Button(navigation_frame, text='\u2605', command=button_bookmark_command)
button_bookmark.grid(column=0, row=0)

button_previous = tk.Button(navigation_frame, text='<', command=button_previous_command)
button_previous.grid(column=1, row=0)

jump_to_row_entry = tk.Entry(navigation_frame, width=5, borderwidth=5)
jump_to_row_entry.bind('<Return>', lambda e: jump_to_row_entry_command())
jump_to_row_entry.grid(column=2, row=0)

row_total_label = tk.Label(navigation_frame, width=5, padx=10)
row_total_label.grid(column=3, row=0)

button_next = tk.Button(navigation_frame, text='>', command=button_next_command)
button_next.grid(column=4, row=0)

viewed_label = tk.Label(navigation_frame, font=('Colibri', 16))
viewed_label.grid(column=5, row=0)

button_jump = tk.Button(navigation_frame, text='>>', command=button_jump_command)
button_jump.grid(column=6, row=0)

bookmarks_total_label = tk.Label(bookmarks_frame)
bookmarks_total_label.grid(column=0, row=0)

button_bookmarks_mode = tk.Button(bookmarks_frame, command=button_bookmarks_mode_command)
button_bookmarks_mode.grid(column=1, row=0)


def groups_match_list_link(groups):
    if groups_match_list.curselection():
        idx = groups_match_list.curselection()[0]
        webbrowser.open('https://vk.com/public{0}'.format(groups[idx][0]))


def groups_list_link(groups):
    if groups_list.curselection():
        idx = groups_list.curselection()[0]
        webbrowser.open('https://vk.com/public{0}'.format(groups[idx][0]))


def music_list_copy(music):
    if music_list.curselection():
        idx = music_list.curselection()[0]
        root.clipboard_clear()
        root.clipboard_append('{0} {1}'.format(music[idx][0], music[idx][1]))
        root.update()


def videos_list_link(videos):
    if videos_list.curselection():
        idx = videos_list.curselection()[0]
        webbrowser.open('{0}'.format(videos[idx][1]))


def filter_string(string):
    string_buf = ''
    for char in string:
        if ord(char) in range(65536):
            string_buf += char
    return string_buf


user = []
bookmarks_mode = False


def update_window():
    global user, bookmarks_total, bookmarks_mode

    user = get_user_by_row(get_row())

    if not bookmarks_mode:
        row_total_label['text'] = '/ {0}'.format(row_total)
    else:
        row_total_label['text'] = '/ {0}'.format(bookmarks_total)

    link_label['text'] = '{0} {1} ({2} лет)'.format(user[1], user[2], user[3])
    link_label.bind('<Double-1>', lambda e: webbrowser.open('https://vk.com/id{0}'.format(user[0])))

    jump_to_row_entry.delete(0, tk.END)
    jump_to_row_entry.insert(0, '{0}'.format(get_row()))

    groups_match_label['text'] = 'Совпадений по группам: {0}'.format(user[7])

    groups_match_list.delete(0, tk.END)
    groups_match_list.bind('<Double-1>', lambda e: groups_match_list_link(user[8]))
    for group in user[8]:
        groups_match_list.insert(tk.END, filter_string(group[1]))

    groups_list.delete(0, tk.END)
    groups_list.bind('<Double-1>', lambda e: groups_list_link(user[4]))
    for group in user[4]:
        groups_list.insert(tk.END, filter_string(group[1]))

    music_list.delete(0, tk.END)
    music_list.bind('<Double-1>', lambda e: music_list_copy(user[6]))
    for audio in user[6]:
        music_list.insert(tk.END, filter_string('{0} - {1}'.format(audio[0], audio[1])))

    videos_list.delete(0, tk.END)
    videos_list.bind('<Double-1>', lambda e: videos_list_link(user[5]))
    for video in user[5]:
        videos_list.insert(tk.END, filter_string('{0}'.format(video[0])))

    if not bookmarks_mode:
        button_jump.grid()
        viewed_label.grid()
        if get_viewed(get_row()):
            viewed_label['text'] = 'Seen'
            viewed_label['fg'] = 'red'
        else:
            viewed_label['text'] = 'New'
            viewed_label['fg'] = 'green'
            set_viewed(get_row(), True)
    else:
        button_jump.grid_remove()
        viewed_label.grid_remove()

    if get_bookmark(user[0]):
        button_bookmark['bg'] = 'green'
    else:
        button_bookmark['bg'] = 'red'

    bookmarks_total_label['text'] = 'Bookmarks: {0}'.format(bookmarks_total)

    if bookmarks_mode:
        button_bookmarks_mode['text'] = 'Close bookmarks'
    else:
        button_bookmarks_mode['text'] = 'Open bookmarks'


update_window()

root.mainloop()
