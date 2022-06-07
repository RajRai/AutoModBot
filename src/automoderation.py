import datetime
import discord
import pytz
import requests
from discord import *
from config.config import settings
from thefuzz import fuzz
from private import TOKEN

import queries

if __name__ == "__main__":
    message = 'p a n d a s are bad painters'
    filter = "drain"
    for word in message.split() + [message.replace(" ", "")]:
        print(f'{word} - {fuzz.ratio(filter, word.lower())}')
        print(f'{word} - {fuzz.partial_ratio(filter, word.lower()) if len(filter) < len(word) else 0}')
        print(f'{word} - {fuzz.token_set_ratio(filter, word.lower()) if " " not in filter else 0}')

seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}


def convert_to_seconds(s):
    return int(s[:-1]) * seconds_per_unit[s[-1]]


def check_blacklist(message: Message) -> (bool, str):
    lo_settings = settings.automod.backlist
    for rule in lo_settings.rules:
        for word in message.content.split() + [message.content.replace(" ", ""), message.content]:
            if rule.exact:
                if rule.content.lower() == word.lower() or rule.content.lower() in word.lower():
                    return True, f'EXACT - {rule.content}', rule
            else:
                ratio = fuzz.ratio(rule.content.lower(), word.lower())
                if ratio > rule.threshold:
                    return True, f'FUZZY RATIO - {rule.content} - Score: {ratio}', rule
        ratio = fuzz.partial_ratio(rule.content.lower(), message.content.lower())
        if ratio > rule.threshold and len(rule.content) < len(message.content):
            return True, f'FUZZY PARTIAL RATIO - {rule.content} - Score: {ratio}', rule
        ratio = fuzz.token_set_ratio(rule.content, message.content)
        if ratio > rule.threshold and ' ' not in rule.content:  # If a space is included, don't filter sub words independently
            return True, f'TOKEN SET RATIO - {rule.content} - Score: {ratio}', rule
    return False, '', None


def check_frequency_limited(message: Message, messages, rule, out_arr, discriminant):
    cutoff = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(
        seconds=convert_to_seconds(rule.cutoff))
    for old in messages[::-1]:
        if pytz.UTC.localize(datetime.datetime.strptime(old[1][:-4], '%Y-%m-%d %H:%M:%S')) < cutoff:
            break
        if discriminant(old, message):
            out_arr.append(old)
    return len(out_arr) >= rule.limit, out_arr, rule


def check_spam(message: Message):
    messages = queries.get_messages(0)  # Replace 0 with message.author.id
    for rule in settings.automod.repeat.rules:
        spam = []
        result = check_frequency_limited(message, messages, rule, spam, discriminant=lambda: True)
        if result[0]:
            return result
    return False, [], None


def check_repeat(message: Message):
    messages = queries.get_messages(0)  # Replace 0 with message.author.id
    for rule in settings.automod.repeat.rules:
        repeated = []
        result = check_frequency_limited(message, messages, rule, repeated,
                                         discriminant=lambda s1, s2: fuzz.ratio(s1.content.lower(),
                                                                                s2.content.lower()) > rule.threshold)
        if result[0]:
            return result
    return False, [], None


def check_mentions(message: Message):
    if len(message.mentions) + len(message.role_mentions) > 0 or message.mention_everyone:
        return None
    messages = queries.get_mentions(message.author.id)
    for rule in settings.automod.mentions.rules:
        if (rule.content.lower() not in message.mentions or rule.content.lower() not in message.role_mentions
                or (rule.content.lower() == 'everyone' and not message.mention_everyone)):
            return False, [], None
        mentions = []
        cutoff = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(
            seconds=convert_to_seconds(rule.cutoff))
        for old in messages[::-1]:
            if pytz.UTC.localize(datetime.datetime.strptime(old[1][:-4], '%Y-%m-%d %H:%M:%S')) < cutoff:
                break
            if rule.content.lower() in old[0].lower() or rule.content.lower() in old[1].lower() or (
                    rule.content.lower() == 'everyone' and old[2] == 1):
                mentions.append(old)
        if len(mentions) >= rule.limit - 1:
            return True, mentions, rule
    return False, []


def get_timeout_from_name(name: str):
    for timeout in settings.automod.timeout:
        if timeout.name.lower() == name.lower():
            return timeout


def get_timeout_duration(user, rule):
    config = get_timeout_from_name(rule.timeout)
    offenses = queries.get_offense_count(user)
    for step in config.steps:
        if offenses < step.offenseCount:
            continue
        duration_seconds = convert_to_seconds(step.timeout)
        return duration_seconds


def log_timeout(message, duration, reason, info):
    user = message.author
    queries.log_timeout(user.id, duration, reason, message.content)
    out = f'Handled message and timed out user {str(user)} ({user.nick}) with duration {duration} for reason: **{reason}**.\n' \
          f'Message: {message}\n' \
          f'Info: \n'
    if reason == 'profanity':
        out += f'```Blacklist entry: {info[2].content}```'
    elif reason == 'spam' or reason == 'repeated messages':
        out += '```'
        for message in info[1]:
            out += f'{message[1]} - {message[0]}\n'
        out += '```'
    elif reason == 'mass-mentions':
        out += '```'
        for message in info[1]:
            out += f'{message[4]} - {message[3]}\n'
        out += '```'
    ch = discord.utils.get(message.guild.text_channels, name=settings.logging_channel)
    ch.send(out)


def timeout_user(user_id: int, guild_id: int, until: int):
    BASE = "https://discord.com/api/v9/"
    endpoint = f'guilds/{guild_id}/members/{user_id}'
    headers = {"Authorization": f"Bot {TOKEN}"}
    url = BASE + endpoint
    timeout = (datetime.datetime.utcnow() + datetime.timedelta(minutes=until)).isoformat()
    json = {'communication_disabled_until': timeout}
    session = requests.patch(url, json=json, headers=headers)
    if session.status_code in range(200, 299):
        return session.json()


def give_timeout(message: Message, time: int, reason: str, info: tuple):
    timeout_user(message.author.id, message.guild.id, int(time / 60))
    out = f'You were given a timeout of {int(time / 60)} minutes for the following reason: **{reason}**.\n' \
          f'Your message: {message}'
    log_timeout(message, time, reason, info)
    message.author.send(out)


def auto_moderate(message: Message):
    flags = {  # Tuple(bool, whatever other information gets returned, ... )
        'blacklist': None,
        'spam': None,
        'repeat': None,
        'mentions': None
    }

    if settings.blacklist.enabled:
        flags['blacklist'] = check_blacklist(message)
    if settings.repeated.enabled:
        flags['repeat'] = check_repeat(message)
    if settings.spam.enabled:
        flags['spam'] = check_spam(message)
    if settings.mentions.enabled:
        flags['mentions'] = check_mentions(message)

    if flags['blacklist'][0]:
        give_timeout(message, get_timeout_duration(message.author.id, flags['blacklist'][2]), 'profanity',
                     flags['blacklist'])
    if flags['repeat'][0]:
        give_timeout(message, get_timeout_duration(message.author.id, flags['repeat'][2]), 'repeated messages',
                     flags['repeat'])
    if flags['spam'][0]:
        give_timeout(message, get_timeout_duration(message.author.id, flags['spam'][2]), 'spam',
                     flags['spam'])
    if flags['mentions'][0]:
        give_timeout(message, get_timeout_duration(message.author.id, flags['mentions'][2]), 'mass-mentions',
                     flags['mentions'])

