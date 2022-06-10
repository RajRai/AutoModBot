import json
import threading
from quart_discord import DiscordOAuth2Session
from src.bot import main, bot, log_setting_change
from quart import Quart, render_template, request, redirect, url_for
from config.private import SECRET_KEY, CLIENT_ID, CLIENT_SECRET
import config.config as config

app = Quart(__name__)

app.config["SECRET_KEY"] = SECRET_KEY
app.config["DISCORD_CLIENT_ID"] = CLIENT_ID  # Discord client ID.
app.config["DISCORD_CLIENT_SECRET"] = CLIENT_SECRET  # Discord client secret.
app.config["DISCORD_REDIRECT_URI"] = "http://localhost:5000/callback"
discordOAuth = DiscordOAuth2Session(app)


async def verify_authorized(guild_id):
    if not await discordOAuth.authorized:
        return False
    await bot.wait_until_ready()
    glds = bot.guilds
    user = await discordOAuth.fetch_user()

    settings = config.settings_for_guild_dict(guild_id)

    for guild in glds:
        member = guild.get_member(user.id)
        if guild.id == guild_id and member is not None:
            if member.top_role.permissions.administrator:
                return True
            if settings is None or 'manager_role' not in settings:
                return False
            for role in settings['manager_role']:
                if role == '':
                    continue
                if role[0] == '@':  # Signals that we should use the permissions attribute
                    try:
                        if getattr(member.top_role.permissions, role[1:].lower()):
                            return True
                    except Exception:
                        pass
                elif role.lower() in [r.name.lower() for r in member.roles]:
                    return True
    return False


@app.route("/login")
async def login():
    return await discordOAuth.create_session(prompt=False)


@app.route("/callback")
async def callback():
    try:
        await discordOAuth.callback()
    except Exception:
        pass

    return redirect(url_for("guilds"))


@app.route("/guilds")
async def guilds():
    if not await discordOAuth.authorized:
        return redirect(url_for('login'))
    await bot.wait_until_ready()
    glds = bot.guilds
    managing = []
    for guild in glds:
        if await verify_authorized(guild.id):
            managing.append({'name': guild.name, 'id': str(guild.id)})
    return await render_template('guilds.html', guilds=json.dumps(managing))


@app.route("/settings/<int:guild_id>", methods=['GET', 'POST'])
async def settings(guild_id: int):
    if not await discordOAuth.authorized or not await verify_authorized(guild_id):
        return redirect(url_for('guilds'))

    if request.method == 'POST' and request.is_json:
        config.replace_settings_for_guild(guild_id, await request.json)
        await log_setting_change(guild_id, await discordOAuth.fetch_user())

    sett = config.settings_for_guild_dict(guild_id)
    return await render_template('settings.html', settings=json.dumps(sett))


def init():
    webApp = threading.Thread(target=app.run)
    webApp.start()
    main()
    webApp.join()


if __name__ == "__main__":
    init()
