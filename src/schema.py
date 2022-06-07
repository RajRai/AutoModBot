from queries import *

if __name__ == "__main__":
    drop = """DROP TABLE IF EXISTS SETTINGS"""
    execute(drop)
    drop = """DROP TABLE IF EXISTS MESSAGES"""
    execute(drop)
    drop = """DROP TABLE IF EXISTS TIMEOUTS"""
    execute(drop)

    table = """ CREATE TABLE IF NOT EXISTS SETTINGS (
                guild INTEGER PRIMARY KEY,
                prefix CHAR(1) DEFAULT '!',
                enabled INTEGER(1) DEFAULT 1
            ); """
    execute(table)

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
                duration,
                reason VARCHAR,
                message VARCHAR,
                PRIMARY KEY (time, user)
            ); """
    execute(table)

    data = """INSERT INTO SETTINGS (guild) VALUES (191217347975970817)"""
    execute(data)

    data = """INSERT INTO MESSAGES (user, message) VALUES (0, 'test1')"""
    execute(data)
    data = """INSERT INTO MESSAGES (user, message) VALUES (0, 'test2')"""
    execute(data)
    data = """INSERT INTO MESSAGES (user, message) VALUES (0, 'test3')"""
    execute(data)


