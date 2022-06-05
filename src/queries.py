import sqlite3
from discord import *
from discord.ext.commands import Context
from config.config import DB_FILE, settings
import automoderation


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


def get_setting(columns, guild: int):
    return select(f"""SELECT {columns} FROM SETTINGS WHERE guild = {guild}""")


def prefix(bot, message):
    id = message.guild.id
    result = get_setting("guild, prefix", id)
    return result[0][1] if len(result) > 0 else None


def get_messages(user):
    rows = select(f"""SELECT message, time FROM MESSAGES WHERE user = {user}""")
    return list(rows)


def store_message(message: Message):
    execute(f"""INSERT INTO MESSAGES (user, message, mentions) VALUES ({message.author.id},{message.content})""")


def prune_history(id):
    count = select(f"""SELECT COUNT(*) FROM MESSAGES WHERE user = {id}""")[0][0]
    diff = count - settings.automod.saved_messages
    execute(f"""DELETE FROM MESSAGES WHERE rowid IN (SELECT rowid FROM MESSAGES WHERE user = {id} LIMIT {diff} )""")


def is_enabled(message: Message):
    return get_setting("enabled", message.guild.id)[0][0] == 1


def set_enabled(ctx: Context, value: bool):
    execute(f"""UPDATE SETTINGS SET enabled = {1 if value else 0} WHERE guild = {ctx.guild.id}""")


if __name__ == "__main__":
    print(automoderation.check_repeated("test"))
