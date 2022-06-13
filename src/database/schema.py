from src.database.queries import *


def init():
    table = """ CREATE TABLE IF NOT EXISTS MESSAGES (
                time DATETIME DEFAULT(STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')),
                user INTEGER NOT NULL,
                message VARCHAR,
                user_mentions VARCHAR default '',
                role_mentions VARCHAR default '',
                mentions_everyone INTEGER(1) default 0,
                PRIMARY KEY (time, user)
            ); """
    execute(table)

    table = """ CREATE TABLE IF NOT EXISTS TIMEOUTS (
                time DATETIME DEFAULT(STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')),
                user INTEGER NOT NULL,
                guild INTEGER NOT NULL,
                duration,
                reason VARCHAR,
                message VARCHAR,
                PRIMARY KEY (time, user, guild)
            ); """
    execute(table)


def clean():
    drop = """DROP TABLE IF EXISTS MESSAGES"""
    execute(drop)
    drop = """DROP TABLE IF EXISTS TIMEOUTS"""
    execute(drop)

    init()


if __name__ == "__main__":
    clean()
