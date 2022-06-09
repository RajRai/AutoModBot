import discord
from discord import *
from config.config import settings_for_guild
from fuzzywuzzy import fuzz


async def log_helper(message, info, rule):
    settings = settings_for_guild(message.guild.id)
    if settings.logging.help_replies:
        out = f'Responded to message by {message.author.mention}\n' \
              f'Message: {message.content}\n' \
              f'Replied: {rule.reply}\n' \
              f'Other info: {info}'
        ch = discord.utils.get(message.guild.text_channels, name=settings.logging.logging_channel)
        await ch.send(out)


async def check_helper(message: Message) -> (bool, str):
    settings = settings_for_guild(message.guild.id)
    if not settings.helper.enabled:
        return
    for rule in settings.helper.rules:
        if not rule.enabled or rule.search is None or rule.threshold is None or rule.reply is None:
            continue
        ratio = fuzz.ratio(rule.search.lower(), message.content.lower())
        if ratio >= rule.threshold * 100:
            await message.reply(rule.reply)
            await log_helper(message, f'FUZZY RATIO - {rule.search} - Score: {ratio}', rule)
            return
        ratio = fuzz.partial_ratio(rule.search.lower(), message.content.lower())
        if ratio >= rule.threshold * 100:
            await message.reply(rule.reply)
            await log_helper(message, f'FUZZY PARTIAL RATIO - {rule.search} - Score: {ratio}', rule)
            return
        ratio = fuzz.token_set_ratio(rule.search, message.content)
        if ratio >= rule.threshold * 100:  # If a space is included, don't filter sub words independently
            await message.reply(rule.reply)
            await log_helper(message, f'TOKEN SET RATIO - {rule.search} - Score: {ratio}', rule)
            return
    return False, '', None