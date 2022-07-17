import asyncio
import json
import sys
import traceback
from asyncio import sleep

import discord
import requests
from discord import *
from discord.ext import commands

from src.bot.modules.autohelper import check_helper
from config.private import TOKEN
import src.database.queries as qr
from src.bot.modules.automoderation import auto_moderate
from config.config import settings_for_guild, settings_for_guild_dict
from config import config

from src.pycord_threaded import ThreadedPycordClient

prefix = config.prefix

intents = discord.Intents.all()
bot = ThreadedPycordClient(command_prefix=prefix, intents=intents)


def is_server_manager(guild: int, user: Member):
    settings = settings_for_guild_dict(guild)
    if user.top_role.permissions.administrator:
        return True
    if 'manager_role' not in settings:
        return False
    for entry in settings['manager_role']:
        if entry == '':
            continue
        if entry[0] == '@':  # Signals that we should use the permissions attribute
            try:
                if getattr(user.top_role.permissions, role[1:].lower()):
                    return True
            except Exception:
                pass
        elif entry.lower() in [r.name.lower() for r in user.roles]:
            return True
        elif entry.lower() == user.name.lower() + '#' + user.discriminator:
            return True
    return user.top_role.permissions.manage_guild


async def update_message_history(message: Message):
    qr.store_message(message)
    settings = settings_for_guild(message.guild.id)
    qr.prune_history(message.author.id, settings.automod.saved_messages)


@bot.event
async def on_message(message: Message):
    await sleep(0.25)
    try:
        if message.author.bot:
            return
        await bot.wait_until_ready()
        await bot.process_commands(message)
        settings = config.settings_for_guild(message.guild.id)
        if settings.enabled and not message.author.top_role.permissions.administrator:
            await auto_moderate(message)
            await update_message_history(message)
            await check_helper(message)
    except Exception:
        traceback.print_exc()


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("A required argument for that command is missing!")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.reply("You lack the permissions to use that command...")
    else:
        await ctx.reply("An unspecified error occurred")
        print(error)


async def log_setting_change(guild_id: int, user: User):  # Thanks Quart
    headers = {
        'Authorization': f'Bot {TOKEN}'
    }
    settings = settings_for_guild(guild_id)
    if not settings.logging.settings_changes:
        return
    channels = json.loads(
        json.dumps(requests.get(f'https://discord.com/api/v10/guilds/{guild_id}/channels', headers=headers).json()))
    for channel in channels:
        if channel['name'] == settings.logging.logging_channel:
            member = None
            for guild in bot.guilds:
                if guild_id == guild.id:
                    member = guild.get_member(user.id)
            if member is not None:
                data = {'content': f'Settings changed via web UI by user: ' + member.mention}
                requests.post(f'https://discord.com/api/v10/channels/{channel["id"]}/messages', data=data,
                              headers=headers).json()


def parse_mode():
    global debug
    try:
        for arg in sys.argv:
            if arg in ("-d", "--debug"):
                debug = True
                print("Enabled debugging mode")
    except Exception as err:
        print(str(err))


def close():
    bot.close()


async def main_async():
    parse_mode()
    await bot.start(TOKEN)


def main():
    parse_mode()
    bot.run(TOKEN)


if __name__ == "__main__":
    main()

# noinspection PyUnresolvedReferences
import src.bot.commands as cmds  # D: (fix for circular import, dont remove)
