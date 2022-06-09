import sys
import discord
from discord import *
from discord.ext import commands
from src.private import TOKEN
import src.queries as qr
from src.automoderation import auto_moderate
from config.config import settings_for_guild

prefix = qr.prefix

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=prefix, intents=intents)

logging_queue = {}  # Lol


def is_dev(ctx):
    return ctx.author.id == 296153936665247745


def is_server_manager(ctx):
    return ctx.author.top_role.permissions.manage_guild


def is_bot_manager(ctx):
    return is_dev(ctx) or is_server_manager(ctx)


@bot.command(name='guilds')
@commands.check(is_dev)
async def guilds(ctx, *words):
    await ctx.reply(" ".join([str(g.id) for g in bot.guilds]))


@bot.command(name='disable', help="Disables the bot's automoderation features")
@commands.check(is_bot_manager)
async def disable(ctx, *words):
    qr.set_enabled(ctx, False)


@bot.command(name='enable', help="Enables the bot's automoderation features")
@commands.check(is_bot_manager)
async def enable(ctx, *words):
    qr.set_enabled(ctx, True)


@bot.command(name='status', help="Sets the bot's status text, with an online status")
@commands.check(is_bot_manager)
async def status(ctx, *words):
    activity = discord.Game(name=" ".join(words))
    await bot.change_presence(status=discord.Status.online, activity=activity)


@bot.command(name='idlestatus', help="Sets the bot's status text, with an idle status")
@commands.check(is_bot_manager)
async def idlestatus(ctx, *words):
    activity = discord.Game(name=" ".join(words))
    await bot.change_presence(status=discord.Status.idle, activity=activity)


async def update_message_history(message: Message):
    qr.store_message(message)
    qr.prune_history(message.author.id, settings_for_guild(message.guild.id).automod.saved_messages)


@bot.event
async def on_guild_join(guild: Guild):
    qr.initialize_settings(guild.id)


@bot.event
async def on_ready():
    for guild in bot.guilds:
        qr.initialize_settings(guild.id)


@bot.event
async def on_socket_event_type(event_type):  # Really just a hack until I can get Quart/Pycord threads to cooperate
    for guild_id in logging_queue:
        settings = settings_for_guild(guild_id)
        for guild in bot.guilds:
            if guild.id != guild_id:
                continue
            ch = discord.utils.get(guild.text_channels, name=settings.logging.logging_channel)
            for msg in logging_queue:
                await ch.send(msg)
        logging_queue[guild_id] = []


@bot.event
async def on_message(message: Message):
    global logging_queue
    if message.author.bot:
        return
    await bot.wait_until_ready()
    await bot.process_commands(message)
    if qr.is_enabled(message) and not message.author.top_role.permissions.administrator:
        await auto_moderate(message)
    await update_message_history(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("A required argument for that command is missing!")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.reply("You lack the permissions to use that command...")
    else:
        await ctx.reply("An unspecified error occurred")


async def log_setting_change(guild_id: int, user: User):
    for guild in bot.guilds:
        if guild.id == guild_id:
            settings = settings_for_guild(guild_id)
            member = guild.get_member(user.id)
            for channel in guild.channels:
                if channel.name.lower() == settings.logging.logging_channel:
                    if logging_queue[guild_id] is None:
                        logging_queue[guild_id] = []
                    logging_queue[guild_id].append(f'Settings changed via web UI by user: ' + member.mention)


def parse_mode():
    global debug
    try:
        for arg in sys.argv:
            if arg in ("-d", "--debug"):
                debug = True
                print("Enabled debugging mode")
    except Exception as err:
        print(str(err))


async def main_async():
    parse_mode()
    bot.run(TOKEN)


def main():
    parse_mode()
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
