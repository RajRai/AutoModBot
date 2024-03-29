from config.config import settings_for_guild
from discord import *
import src.database.queries as queries
import datetime
import discord


async def notify_timeout_deletion(message: Message, timeouts: dict):
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


def generate_info(reason: str, info: dict, message: str = ''):
    out = ''
    if reason == 'profanity':
        out = f'Blacklist entry: {info["rule"].content}\n' \
              f'Message: {message}\n' \
              f'{info["info"]}'
    elif reason in ['spam', 'repeated messages', 'mass-mentions']:
        out = ''
        for msg in info["messages"]:
            out += f'Time: {msg["time"]} - Message: {msg["message"]}\n'
    return out


async def log_timeout(message: Message, duration: int, reason: str, info: dict):
    settings = settings_for_guild(message.guild.id)
    offenses = queries.get_offenses(message.author.id, message.guild.id)[:15]
    user = message.author
    queries.log_timeout(user.id, message.guild.id, duration, reason, message.content)
    if settings.logging.timeouts and duration > 0 or settings.logging.deletes:
        off_fmt = '\n'.join([f"Date: {o[0]}, Duration (s): {o[3]}, Reason: {o[4]}, Message: {o[5]}" for o in offenses])
        out = f'Deleted message and timed out user {user.mention}' \
              f'with duration {duration / 60:.2f}m for reason: **{reason}**.\n' \
              f'Message: {message.content}\n' \
              f'Time: {datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")}\n' \
              f'Previous offenses: ```{off_fmt}```\n' \
              f'Info: ```{generate_info(reason, info, message.content)}```\n'
        ch = discord.utils.get(message.guild.text_channels, name=settings.logging.logging_channel)
        await ch.send(out)
    if duration > 0:
        out = f'You were given a timeout of {duration / 60:.2f} minutes for the following reason: **{reason}**.\n' \
              f'Your message: {message.content}'
        await message.author.send(out)


async def log_ban(message: Message, reason: str, info: dict):
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
