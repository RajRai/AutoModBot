import datetime

import pytz
from discord import *
from config.config import settings
from thefuzz import fuzz

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
                    return True, f'EXACT - {rule.content}'
            else:
                ratio = fuzz.ratio(rule.content.lower(), word.lower())
                if ratio > rule.limit:
                    return True, f'FUZZY RATIO - {rule.content} - Score: {ratio}'
        ratio = fuzz.partial_ratio(rule.content.lower(), message.content.lower())
        if ratio > rule.limit and len(rule.content) < len(message.content):
            return True, f'FUZZY PARTIAL RATIO - {rule.content} - Score: {ratio}'
        ratio = fuzz.token_set_ratio(rule.content, message.content)
        if ratio > rule.limit and ' ' not in rule.content:  # If a space is included, don't filter sub words independently
            return True, f'TOKEN SET RATIO - {rule.content} - Score: {ratio}'
    return False, ''


def check_repeated(message: Message, setting=settings.automod.repeat, discriminator=None) -> (bool, list):
    messages = queries.get_messages(0)  # Replace 0 with message.author.id
    lo_settings = setting
    for rule in lo_settings.rules:
        cutoff = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(
            seconds=convert_to_seconds(rule.cutoff))
        count = 0
        repeated = []
        ret = False
        if discriminator is None:
            discriminator = lambda s1, s2: fuzz.ratio(s1, s2) > rule.limit
        for old in messages:
            if pytz.UTC.localize(datetime.datetime.strptime(old[1][:-4], '%Y-%m-%d %H:%M:%S')) < cutoff:
                continue
            if discriminator(old[0].lower(), message.lower()):
                count += 1
                repeated.append(old)
            if count >= rule.messages:
                ret = True
        if ret:
            return ret, repeated
    return False, []


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
        flags['repeat'] = check_repeated(message)
    if settings.spam.enabled:
        flags['spam'] = check_repeated(message, setting=settings.automod.spam, discriminator=lambda: True)
