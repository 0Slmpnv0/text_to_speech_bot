from icecream import ic
from config import MAX_SYMBOLS_PER_USER
import sqlite3


def init() -> None:
    sql = '''CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    chars_remaining INTEGER
    );'''
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    conn.close()


def update_user_chars(user_id, chars) -> None:
    sql = '''UPDATE users SET chars_remaining = ? WHERE user_id = ?'''
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    cur.execute(sql, (chars, user_id))
    conn.commit()
    conn.close()


def rm_table(name) -> None:
    sql = f'''DROP TABLE {name}'''
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    conn.close()


def get_users() -> list[dict[str: str | int]] | None | dict[str: str | int]:
    sql = '''SELECT user_id, chars_remaining FROM users'''
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    res = [dict(res) for res in cur.execute(sql)]
    if not res:
        return None
    conn.close()
    return res


def add_user(user_id, chars=MAX_SYMBOLS_PER_USER):
    sql = '''INSERT INTO users (user_id, chars_remaining) values (?, ?)'''
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    cur.execute(sql, (user_id, chars))
    conn.commit()
    conn.close()


def get_user_chars(uid) -> int:
    sql = '''SELECT chars_remaining FROM users WHERE user_id=?'''
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    res = [dict(res) for res in cur.execute(sql, (uid, ))]
    if not res:
        return MAX_SYMBOLS_PER_USER
    conn.close()
    return res['chars_remaining']
