from src.bot.bot import bot, is_server_manager
from discord.ext import commands
from config.config import *
import discord
import src.bot.modules.automoderation as am


def is_dev(ctx):
    return ctx.author.id == 296153936665247745


def is_server_manager_ctx(ctx):
    return is_server_manager(ctx.guild.id, ctx.author)


@bot.command(name='guilds')
@commands.check(is_dev)
async def guilds(ctx, *words):
    await ctx.reply(" ".join([str(g.id) for g in bot.guilds]))


@bot.command(name='untimeout', help='Removes a user from the timeout list')
@commands.check(is_server_manager)
async def untimeout(ctx, *words):
    guild_id = ctx.guild.id
    users = [user_mentioned.id for user_mentioned in ctx.message.mentions]
    for user in users:
        am.lift_timeout(user, guild_id)


@bot.command(name='disable', help="Disables the bot's automoderation features")
@commands.check(is_server_manager)
async def disable(ctx, *words):
    settings = settings_for_guild_dict(ctx.guild.id)
    settings['enabled'] = False
    replace_settings_for_guild(ctx.guild.id, settings)


@bot.command(name='enable', help="Enables the bot's automoderation features")
@commands.check(is_server_manager)
async def enable(ctx, *words):
    settings = settings_for_guild_dict(ctx.guild.id)
    settings['enabled'] = True
    replace_settings_for_guild(ctx.guild.id, settings)


@bot.command(name='status', help="Sets the bot's status text, with an online status")
@commands.check(is_dev)
async def status(ctx, *words):
    activity = discord.Game(name=" ".join(words))
    await bot.change_presence(status=discord.Status.online, activity=activity)


@bot.command(name='idlestatus', help="Sets the bot's status text, with an idle status")
@commands.check(is_dev)
async def idlestatus(ctx, *words):
    activity = discord.Game(name=" ".join(words))
    await bot.change_presence(status=discord.Status.idle, activity=activity)
