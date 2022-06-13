from config.config import settings_for_guild
from discord import *
import src.database.queries as queries
import datetime
import discord
from src.bot.modules.automoderation import timeouts


async def notify_timeout_deletion(message: Message):
    settings = settings_for_guild(message.guild.id)
    timeout = timeouts[message.author.id, message.guild.id]
    time = timeout[0] - datetime.datetime.utcnow()
    if settings.logging.deletes:
        out = f'Deleted message by {message.author.mention} due to ongoing timeout.\n' \
              f'Message: {message.content}\n' \
              f'Timeout remaining: {time.total_seconds() / 60:.2f} minutes remaining'
        ch = discord.utils.get(message.guild.text_channels, name=settings.logging.logging_channel)
        await ch.send(out)
    out = f'You still have a timeout of {time.total_seconds() / 60:.2f} minutes for the following reason: **{timeout[1]}**.\n' \
          f'Your message: {timeout[2]}'
    await message.author.send(out)


def generate_info(reason: str, info: dict):
    out = ''
    if reason == 'profanity':
        out = f'Blacklist entry: {info["rule"].content}\n' \
               f'Message: {message.content}\n' \
               f'{info["info"]}```'
    elif reason == 'spam' or reason == 'repeated messages':
        out = ''
        for msg in info["messages"]:
            out += f'{msg["time"]} - {msg["message"]}\n'
    elif reason == 'mass-mentions':
        out = ''
        for msg in info["messages"]:
            out += f'{msg["time"]} - {msg["message"]}\n'
    return out


async def log_timeout(message: Message, duration: int, reason: str, info: dict):
    settings = settings_for_guild(message.guild.id)
    offenses = queries.get_offenses(message.author.id, message.guild.id)
    user = message.author
    queries.log_timeout(user.id, message.guild.id, duration, reason, message.content)
    if settings.logging.timeouts and duration > 0 or settings.logging.deletes:
        out = f'Deleted message and timed out user {user.mention}' \
              f'with duration {duration / 60:.2f}m for reason: **{reason}**.\n' \
              f'Message: {message.content}\n' \
              f'Time: {datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%f")}\n' \
              f'Previous offenses: ```{offenses}```\n' \
              f'Info:\n ```{generate_info(reason, info)}```\n'
        ch = discord.utils.get(message.guild.text_channels, name=settings.logging.logging_channel)
        await ch.send(out)
    if duration > 0:
        out = f'You were given a timeout of {duration / 60:.2f} minutes for the following reason: **{reason}**.\n' \
              f'Your message: {message.content}'
        await message.author.send(out)


def log_ban(message: Message, reason: str, info: dict):
    settings = settings_for_guild(message.guild.id)
    offenses = queries.get_offenses(message.author.id, message.guild.id)
    out = f' banned from the server.' \
          f'Message: {message.content}\n' \
          f'Time: {datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%f")}\n' \
          f'Previous offenses: ```{offenses}```\n' \
          f'Info:\n ```{generate_info(reason, info)}```\n'
    if settings.logging.bans:
        ch = discord.utils.get(message.guild.text_channels, name=settings.logging.logging_channel)
        await ch.send(f'{message.author.mention} was' + out)
    await message.author.send('You were' + out)
