import sqlite3
from discord import *
from config import DB_FILE
from settings import settings


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


def prefix(bot, message):
    id = message.guild.id
    result = select(f"""SELECT guild, prefix FROM SETTINGS WHERE guild = {id}""")
    return result[0][1] if len(result) > 0 else None


def store_message(message: Message):
    execute(f"""INSERT INTO MESSAGES (user, message) VALUES ({message.author.id},{message.content})""")


def prune_history(id):
    count = select(f"""SELECT COUNT(*) FROM MESSAGES WHERE user = {id}""")[0][0]
    diff = count - settings.automod.prune_message_threshold
    execute(f"""DELETE FROM MESSAGES WHERE rowid IN (SELECT rowid FROM MESSAGES WHERE user = {id} LIMIT {diff} )""")


if __name__ == "__main__":
    prune_history(0)
