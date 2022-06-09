import datetime
import discord
import pytz
from discord import *
from config.config import settings_for_guild
from thefuzz import fuzz

import src.queries as queries

if __name__ == "__main__":
    message = 'p a n d a s are bad painters'
    filter = "drain"
    for word in message.split() + [message.replace(" ", "")]:
        print(f'{word} - {fuzz.ratio(filter, word.lower())}')
        print(f'{word} - {fuzz.partial_ratio(filter, word.lower()) if len(filter) < len(word) else 0}')
        print(f'{word} - {fuzz.token_set_ratio(filter, word.lower()) if " " not in filter else 0}')

seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}

timeouts = {}


def convert_to_seconds(s):
    if s == '':
        return 0
    return int(s[:-1]) * seconds_per_unit[s[-1]]


def check_blacklist(message: Message) -> (bool, str):
    settings = settings_for_guild(message.guild.id)
    for rule in settings.automod.blacklist.rules:
        for word in message.content.split() + [message.content.replace(" ", ""), message.content]:
            if rule.exact:
                if rule.content.lower() == word.lower() or rule.content.lower() in word.lower():
                    return True, f'EXACT - {rule.content}', rule
            else:
                ratio = fuzz.ratio(rule.content.lower(), word.lower())
                if ratio >= rule.threshold * 100:
                    return True, f'FUZZY RATIO - {rule.content} - Score: {ratio}', rule
        ratio = fuzz.partial_ratio(rule.content.lower(), message.content.lower())
        if ratio >= rule.threshold * 100 and len(rule.content) < len(message.content):
            return True, f'FUZZY PARTIAL RATIO - {rule.content} - Score: {ratio}', rule
        ratio = fuzz.token_set_ratio(rule.content, message.content)
        if ratio >= rule.threshold * 100 and ' ' not in rule.content:  # If a space is included, don't filter sub words independently
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
    settings = settings_for_guild(message.guild.id)
    messages = queries.get_messages(message.author.id)
    for rule in settings.automod.spam.rules:
        if rule.limit is None:
            continue
        spam = []
        result = check_frequency_limited(message, messages, rule, spam, discriminant=lambda x, y: True)
        if result[0]:
            return result
    return False, [], None


def check_repeat(message: Message):
    settings = settings_for_guild(message.guild.id)
    messages = queries.get_messages(message.author.id)
    for rule in settings.automod.repeat.rules:
        repeated = []
        result = check_frequency_limited(message, messages, rule, repeated,
                                         discriminant=lambda s1, s2: fuzz.ratio(s1[0].lower(),
                                                                                s2.content.lower()) >= rule.threshold * 100)
        if result[0]:
            return result
    return False, [], None


def check_mentions(message: Message):
    settings = settings_for_guild(message.guild.id)
    if len(message.mentions) + len(message.role_mentions) > 0 or message.mention_everyone:
        return None
    messages = queries.get_mentions(message.author.id)
    for rule in settings.automod.mentions.rules:
        mentions = []
        for role in rule.content:
            if (role.lower() not in message.mentions or role.lower() not in message.role_mentions
                    or (role.lower() == 'everyone' and not message.mention_everyone)):
                return False, [], None
            cutoff = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(
                seconds=convert_to_seconds(rule.cutoff))
            for old in messages[::-1]:
                if pytz.UTC.localize(datetime.datetime.strptime(old[1][:-4], '%Y-%m-%d %H:%M:%S')) < cutoff:
                    break
                if role.lower() in old[0].lower() or role.lower() in old[1].lower() or (
                        role.lower() == 'everyone' and old[2] == 1):
                    mentions.append(old)
        if len(mentions) >= rule.limit - 1:
            return True, mentions, rule
    return False, []


def get_timeout_from_name(name: str, settings):
    for timeout in settings.automod.timeout:
        if timeout.name.lower() == name.lower():
            return timeout


def get_timeout_duration(user, rule, settings):
    config = get_timeout_from_name(rule.timeout, settings)
    offenses = queries.get_offenses(user)
    duration_seconds = 0
    for step in config.steps:
        if len(offenses) >= step.offenseCount:
            if step.timeout == 'ban':
                return 'ban'
            duration_seconds = convert_to_seconds(step.timeout)
    return duration_seconds


async def log_timeout(message, duration, reason, info):
    settings = settings_for_guild(message.guild.id)
    user = message.author
    queries.log_timeout(user.id, duration, reason, message.content)
    out = f'Deleted message and timed out user {user.mention}' \
          f'with duration {duration / 60:.2f}m for reason: **{reason}**.\n' \
          f'Message: {message.content}\n' \
          f'Time: {datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%f")}\n' \
          f'Info: \n'
    if reason == 'profanity':
        out += f'```Blacklist entry: {info[2].content}\n' \
               f'Message: {message.content}\n' \
               f'{info[1]}```'
    elif reason == 'spam' or reason == 'repeated messages':
        out += '```'
        for msg in info[1]:
            out += f'{msg[1]} - {msg[0]}\n'
        out += '```'
    elif reason == 'mass-mentions':
        out += '```'
        for msg in info[1]:
            out += f'{msg[4]} - {msg[3]}\n'
        out += '```'
    ch = discord.utils.get(message.guild.text_channels, name=settings.logging.logging_channel)
    await ch.send(out)


async def give_ban(message: Message, reason: str, info: tuple):
    settings = settings_for_guild(message.guild.id)
    offenses = queries.get_offenses(message.author.id)
    out = f' banned from the server.' \
          f'Message: {message.content}\n' \
          f'Time: {datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%f")}\n' \
          f'Previous offenses: ```{offenses}```' \
          f'Info: \n'
    if reason == 'profanity':
        out += f'```Blacklist entry: {info[2].content}\n' \
               f'Message: {message.content}\n' \
               f'{info[1]}```'
    elif reason == 'spam' or reason == 'repeated messages':
        out += '```'
        for msg in info[1]:
            out += f'{msg[1]} - {msg[0]}\n'
        out += '```'
    elif reason == 'mass-mentions':
        out += '```'
        for msg in info[1]:
            out += f'{msg[4]} - {msg[3]}\n'
        out += '```'
    if settings.logging.bans:
        ch = discord.utils.get(message.guild.text_channels, name=settings.logging.logging_channel)
        await ch.send(f'{message.author.mention} was' + out)
    await message.author.send('You were' + out)


async def give_timeout(message: Message, reason: str, info: tuple):
    await message.delete()
    settings = settings_for_guild(message.guild.id)
    time = get_timeout_duration(message.author.id, info[2], settings)
    if time == 'ban':
        await give_ban(message, reason, info)
    timeout = datetime.datetime.utcnow() + datetime.timedelta(seconds=time)
    timeouts[(message.author.id, message.guild.id)] = timeout, reason, message.content
    if settings.logging.deletes or settings.logging.timeouts:
        await log_timeout(message, time, reason, info)
    out = f'You were given a timeout of {time / 60:.2f} minutes for the following reason: **{reason}**.\n' \
          f'Your message: {message.content}'
    await message.author.send(out)


async def notify_timeout(message: Message):
    await message.delete()
    settings = settings_for_guild(message.guild.id)
    timeout = timeouts[message.author.id, message.guild.id]
    time = timeout[0] - datetime.datetime.utcnow()
    if settings.logging.deletes:
        out = f'Deleted message by {message.author.mention} due to ongoing timeout.\n' \
              f'Message: {message.content}\n' \
              f'Timeout remaining: {time.total_seconds / 60:.2f} minutes remaining'
        ch = discord.utils.get(message.guild.text_channels, name=settings.logging.logging_channel)
        await ch.send(out)
    out = f'You still have a timeout of {time.total_seconds() / 60:.2f} minutes for the following reason: **{timeout[1]}**.\n' \
          f'Your message: {timeout[2]}'
    await message.author.send(out)


async def auto_moderate(message: Message):
    settings = settings_for_guild(message.guild.id)
    flags = {  # Tuple(bool, whatever other information gets returned, ... )
        'blacklist': None,
        'spam': None,
        'repeat': None,
        'mentions': None
    }

    if (message.author.id, message.guild.id) in timeouts and timeouts[(message.author.id, message.guild.id)][0] \
            > datetime.datetime.utcnow():
        await notify_timeout(message)

    if settings.automod.blacklist.enabled:
        flags['blacklist'] = check_blacklist(message)
    if settings.automod.repeat.enabled:
        flags['repeat'] = check_repeat(message)
    if settings.automod.spam.enabled:
        flags['spam'] = check_spam(message)
    if settings.automod.mentions.enabled:
        flags['mentions'] = check_mentions(message)

    if flags['blacklist'][0]:
        await give_timeout(message, 'profanity', flags['blacklist'])
    if flags['repeat'][0]:
        await give_timeout(message, 'repeated messages', flags['repeat'])
    if flags['spam'][0]:
        await give_timeout(message, 'spam', flags['spam'])
    if flags['mentions'][0]:
        await give_timeout(message, 'mass-mentions', flags['mentions'])
