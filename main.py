import asyncio
import functools
import json
import threading
import time
from config.private import TOKEN
from quart_discord import DiscordOAuth2Session
from src.bot.bot import main, main_async, bot, log_setting_change, is_server_manager
from quart import Quart, render_template, request, redirect, url_for
from src.quart_threaded import ThreadedApp
from config.private import SECRET_KEY, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
import config.config as config
from src.database.schema import init as db_init
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware


# App is behind one proxy that sets the -For and -Host headers.
app = ThreadedApp(__name__)
app.asgi_app = ProxyHeadersMiddleware(app.asgi_app, trusted_hosts=["127.0.0.1", "192.168.0.10"])  # nginx server IP

app.config["SECRET_KEY"] = SECRET_KEY
app.config["DISCORD_CLIENT_ID"] = CLIENT_ID  # Discord client ID.
app.config["DISCORD_CLIENT_SECRET"] = CLIENT_SECRET  # Discord client secret.
app.config["DISCORD_REDIRECT_URI"] = REDIRECT_URI
discordOAuth = DiscordOAuth2Session(app, bot_token=TOKEN)


@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))


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
    return await discordOAuth.create_session(prompt=True)


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


async def init():
    bot_t = threading.Thread(target=main, daemon=True)

    web = threading.Thread(target=app.run, kwargs={
        'port': config.WEB_PORT,
        'host': config.HOST
    })
    web.daemon = True
    web.start()

    bot_t.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Terminating due to Ctrl+C')
        web.join(timeout=0)
        asyncio.get_running_loop().close()


if __name__ == "__main__":
    db_init()
    asyncio.run(init())
