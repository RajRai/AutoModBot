import sys
import discord
from discord import *
from discord.ext import commands
from quart import Quart, render_template, request, session, redirect, url_for
from quart_discord import DiscordOAuth2Session
from private import SECRET_KEY, CLIENT_ID, CLIENT_SECRET, TOKEN
from queries import prefix, store_message, prune_history, is_enabled, set_enabled
from automoderation import auto_moderate

app = Quart(__name__)

app.config["SECRET_KEY"] = SECRET_KEY
app.config["DISCORD_CLIENT_ID"] = CLIENT_ID  # Discord client ID.
app.config["DISCORD_CLIENT_SECRET"] = CLIENT_SECRET  # Discord client secret.
app.config["DISCORD_REDIRECT_URI"] = "http://github.com"

discordOAuth = DiscordOAuth2Session(app)
bot = commands.Bot(command_prefix=prefix)


def is_dev(ctx):
    return ctx.author.id == 296153936665247745


def is_server_manager(ctx):
    return ctx.author.top_role.permissions.manage_guild


def is_bot_manager(ctx):
    return is_dev(ctx) or is_server_manager(ctx)


@bot.command(name='disable', help="Disables the bot's automoderation features")
@commands.check(is_bot_manager)
async def disable(ctx, *words):
    set_enabled(ctx, False)


@bot.command(name='enable', help="Enables the bot's automoderation features")
@commands.check(is_bot_manager)
async def enable(ctx, *words):
    set_enabled(ctx, True)


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
    store_message(message)
    prune_history(message.author.id)


@bot.event
async def on_message(message: Message):
    await bot.wait_until_ready()
    await bot.process_commands(message)
    if is_enabled(message):
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


def parse_mode():
    global debug
    try:
        for arg in sys.argv:
            if arg in ("-d", "--debug"):
                debug = True
                print("Enabled debugging mode")
    except Exception as err:
        print(str(err))

def main():
    parse_mode()
    bot.run(TOKEN)
