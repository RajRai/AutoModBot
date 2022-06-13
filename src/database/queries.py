import sqlite3
from discord import *
from config.config import DB_FILE
import src.bot.modules.automoderation as automod


def _serialize_list(list):
    out = ''
    for x in list:
        out += str(x) + '\t'
    return out.strip()


def _create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
        print(e)
    return conn


def select(query):
    conn = _create_connection(DB_FILE)
    if conn is None:
        return None
    rows = conn.cursor().execute(query).fetchall()
    conn.close()
    return rows


def select_dict(columns: str, table: str, append: str):
    conn = _create_connection(DB_FILE)
    if conn is None:
        return None
    rows = conn.cursor().execute(
        f"""SELECT {columns} from {table} {append}"""
    ).fetchall()
    conn.close()

    result = []

    for r in rows:
        d = {}
        splits = columns.split(',')
        for i in range(len(splits)):
            col = splits[i]
            d[col.strip()] = r[r[i]]
        result.append(r)

    return result


def execute(query):
    conn = _create_connection(DB_FILE)
    if conn is None:
        return
    conn.cursor().execute(query)
    conn.commit()
    conn.close()


def log_timeout(user: int, guild: int, duration: int, reason: str, message: str):
    execute(f"""INSERT INTO TIMEOUTS (user, guild, duration, reason, message)
                VALUES ({user}, {guild}, {duration}, '{reason}', '{message}')""")


def get_offenses(user: int, guild: int):
    return select(f"""SELECT * FROM TIMEOUTS WHERE user = {user} AND guild = {guild}""")


def get_messages(user: int):
    return select_dict(columns="message, time", table="MESSAGES", append=f"WHERE user = {user}")


def get_mentions(user: int):
    return select_dict(columns="user_mentions, role_mentions, mentions_everyone, message, time", table="MESSAGES",
                       append=f"WHERE user = {user}"
                              f"AND (user_mentions != '' OR role_mentions != '' OR mentions_everyone != 0)")


def store_message(message: Message):
    execute(f"""INSERT INTO MESSAGES (user, message, user_mentions, role_mentions, mentions_everyone) 
                VALUES ({message.author.id},'{message.content}','{_serialize_list(message.mentions)}',
                        '{_serialize_list(message.role_mentions)}',{1 if message.mention_everyone else 0})""")


def prune_history(user: int, save: int):
    count = select(f"""SELECT COUNT(*) FROM MESSAGES WHERE user = {user}""")[0][0]
    diff = count - save
    if (diff <= 0):
        return
    execute(f"""DELETE FROM MESSAGES WHERE rowid IN (SELECT rowid FROM MESSAGES WHERE user = {user} LIMIT {diff} )""")


if __name__ == "__main__":
    print(automod.check_repeated("test"))
