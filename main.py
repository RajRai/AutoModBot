import json
import threading
import time

from quart_discord import DiscordOAuth2Session
from src.bot.bot import main, bot, log_setting_change, is_server_manager
from quart import Quart, render_template, request, redirect, url_for
from config.private import SECRET_KEY, CLIENT_ID, CLIENT_SECRET
import config.config as config
from src.database.schema import init as db_init

app = Quart(__name__)

app.config["SECRET_KEY"] = SECRET_KEY
app.config["DISCORD_CLIENT_ID"] = CLIENT_ID  # Discord client ID.
app.config["DISCORD_CLIENT_SECRET"] = CLIENT_SECRET  # Discord client secret.
app.config["DISCORD_REDIRECT_URI"] = "http://localhost:5000/callback"
discordOAuth = DiscordOAuth2Session(app)


async def verify_authorized(guild_id):
    if not await discordOAuth.authorized:
        return False
    if not bot.is_ready():
        return False
    glds = bot.guilds
    user = await discordOAuth.fetch_user()

    for guild in glds:
        member = guild.get_member(user.id)
        if guild.id == guild_id and member is not None:
            return is_server_manager(guild_id, member)
    return False


@app.route("/")
async def home():
    return redirect(url_for("login"))


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
    if not bot.is_ready():
        return 'Refresh'
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
        await log_setting_change(guild_id, await discordOAuth.fetch_user())
        config.replace_settings_for_guild(guild_id, await request.json)

    sett = config.settings_for_guild_dict(guild_id)
    return await render_template('settings.html', settings=json.dumps(sett))


def init():
    web_app = threading.Thread(target=app.run)
    web_app.daemon = True
    bot_t = threading.Thread(target=main)
    bot_t.daemon = True

    web_app.start()
    bot_t.start()

    try:
        while threading.active_count() > 0:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Terminating due to Ctrl+C')


if __name__ == "__main__":
    db_init()
    init()
