import sqlite3
from discord import *
from discord.ext.commands import Context
from config.config import DB_FILE
import src.automoderation as automod


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


def execute(query):
    conn = _create_connection(DB_FILE)
    if conn is None:
        return
    conn.cursor().execute(query)
    conn.commit()
    conn.close()


def initialize_settings(guild: int):
    execute(f"""INSERT INTO SETTINGS (guild) VALUES ({guild})
                ON CONFLICT DO NOTHING""")


def get_setting(columns, guild: int):
    return select(f"""SELECT {columns} FROM SETTINGS WHERE guild = {guild}""")


def prefix(bot, message):
    id = message.guild.id
    result = get_setting("guild, prefix", id)
    return result[0][1] if len(result) > 0 else '!'


def log_timeout(user: int, duration: int, reason: str, message: str):
    execute(f"""INSERT INTO TIMEOUTS (user, duration, reason, message)
                VALUES ({user}, {duration}, '{reason}', '{message}')""")


def get_offenses(user: int):
    return select(f"""SELECT * FROM TIMEOUTS WHERE user = {user}""")[0][0]


def get_messages(user: int):
    rows = select(f"""SELECT message, time FROM MESSAGES WHERE user = {user}""")
    return list(rows)

def get_mentions(user: int):
    return list(select(f"""SELECT user_mentions, role_mentions, mentions_everyone, message, time FROM MESSAGES 
                           WHERE user = {user} 
                           AND (user_mentions != '' OR role_mentions != '' OR mentions_everyone != 0) """))


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


def is_enabled(message: Message):
    return get_setting("enabled", message.guild.id)[0][0] == 1


def set_enabled(ctx: Context, value: bool):
    execute(f"""UPDATE SETTINGS SET enabled = {1 if value else 0} WHERE guild = {ctx.guild.id}""")


if __name__ == "__main__":
    print(automod.check_repeated("test"))
