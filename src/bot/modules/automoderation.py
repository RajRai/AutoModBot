import pytz
from thefuzz import fuzz
from config.config import seconds_per_unit
from src.bot.modules.logging import *
import src.database.queries as queries
from config.config import settings_for_guild
import datetime

if __name__ == "__main__":
    message = 'p a n d a s are bad painters'
    filter = "drain"
    for word in message.split() + [message.replace(" ", "")]:
        print(f'{word} - {fuzz.ratio(filter, word.lower())}')
        print(f'{word} - {fuzz.partial_ratio(filter, word.lower()) if len(filter) < len(word) else 0}')
        print(f'{word} - {fuzz.token_set_ratio(filter, word.lower()) if " " not in filter else 0}')

timeouts = {}


def convert_to_seconds(s):
    if s == '' or s[-1] not in seconds_per_unit or not s[:-1].isdigit():
        return 0
    return int(s[:-1]) * seconds_per_unit[s[-1]]


def check_blacklist(message: Message) -> (bool, str):
    settings = settings_for_guild(message.guild.id)
    for rule in settings.automod.blacklist.rules:
        if not rule.enabled or rule.threshold is None or rule.content == '':
            continue
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
        if pytz.UTC.localize(datetime.datetime.strptime(old['time'][:-4], '%Y-%m-%d %H:%M:%S')) < cutoff:
            break
        if discriminant(old, message):
            out_arr.append(old)
    return len(out_arr) >= rule.limit, out_arr, rule


def check_spam(message: Message):
    settings = settings_for_guild(message.guild.id)
    messages = queries.get_messages(message.author.id)
    for rule in settings.automod.spam.rules:
        if not rule.enabled or rule.limit is None:
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
        if not rule.enabled or rule.limit is None or rule.threshold is None or rule.cutoff is None:
            continue
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
        if not rule.enabled:
            continue
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
        if len(mentions) >= rule.limit:
            return True, mentions, rule
    return False, [], None


def get_timeout_from_name(name: str, settings):
    for timeout in settings.automod.timeout:
        if timeout.name.lower() == name.lower():
            return timeout


def get_timeout_duration(user: int, guild: int, rule, settings):
    config = get_timeout_from_name(rule.timeout, settings)
    if config is None:
        return -1
    offenses_t = queries.get_offenses(user, guild)
    duration_seconds = 0
    for step in config.steps:
        try:
            offenses = []
            cutoff = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(
                seconds=convert_to_seconds(step.cutoff))
            for offense in offenses_t:
                if pytz.UTC.localize(datetime.datetime.strptime(offense[0][:-4], '%Y-%m-%d %H:%M:%S')) > cutoff:
                    offenses.append(offense)
            if len(offenses) >= int(step.offenseCount):
                if step.timeout == 'ban':
                    return 'ban'
                duration_seconds = convert_to_seconds(step.timeout)
        except Exception as e:
            pass
    return duration_seconds


async def give_ban(message: Message, reason: str, info: dict):
    log_ban(message, reason, info)
    await message.author.ban()


async def give_timeout(message: Message, reason: str, info: dict):
    settings = settings_for_guild(message.guild.id)
    time = get_timeout_duration(message.author.id, message.guild.id, info['rule'], settings)
    if time == 'ban':
        await give_ban(message, reason, info)
        return
    if time < 0:
        return
    timeout = datetime.datetime.utcnow() + datetime.timedelta(seconds=time)
    timeouts[(message.author.id, message.guild.id)] = timeout, reason, message.content
    await log_timeout(message, time, reason, info)
    await message.delete()


async def notify_timeout(message: Message):
    await notify_timeout_deletion(message, timeouts)
    await message.delete()


async def auto_moderate(message: Message):
    settings = settings_for_guild(message.guild.id)

    if not settings.automod.enabled:
        return

    flags = {  # Tuple(bool, whatever other information gets returned, ... )
        'blacklist': None,
        'spam': None,
        'repeat': None,
        'mentions': None
    }

    if (message.author.id, message.guild.id) in timeouts and timeouts[(message.author.id, message.guild.id)][0] \
            > datetime.datetime.utcnow():
        await notify_timeout(message)
        return

    if settings.automod.blacklist.enabled:
        result = check_blacklist(message)
        flags['blacklist'] = {
            'flagged': result[0],
            'info': result[1],
            'rule': result[2]
        }
    if settings.automod.repeat.enabled:
        result = check_repeat(message)
        flags['repeat'] = {
            'flagged': result[0],
            'messages': result[1],
            'rule': result[2]
        }
    if settings.automod.spam.enabled:
        result = check_spam(message)
        flags['spam'] = {
            'flagged': result[0],
            'messages': result[1],
            'rule': result[2]
        }
    if settings.automod.mentions.enabled:
        result = check_mentions(message)
        flags['mentions'] = {
            'flagged': result[0],
            'messages': result[1],
            'rule': result[2]
        }

    if flags['blacklist']['flagged']:
        await give_timeout(message, 'profanity', flags['blacklist'])
    elif flags['repeat']['flagged']:
        await give_timeout(message, 'repeated messages', flags['repeat'])
    elif flags['spam']['flagged']:
        await give_timeout(message, 'spam', flags['spam'])
    elif flags['mentions']['flagged']:
        await give_timeout(message, 'mass-mentions', flags['mentions'])


def lift_timeout(user_id, guild_id):
    if (user_id, guild_id) in timeouts:
        del (timeouts[user_id, guild_id])
