import json
import threading
from quart_discord import DiscordOAuth2Session
from src.bot import main
from quart import Quart, render_template, request, session, redirect, url_for
from src.private import SECRET_KEY, CLIENT_ID, CLIENT_SECRET
import config.config as config
from src.bot import bot

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
    for guild in glds:
        member = guild.get_member(user.id)
        if guild.id == guild_id and member is not None:
            if member.top_role.permissions.administrator:
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
    user = await discordOAuth.fetch_user()
    managing = []
    for guild in glds:
        member = guild.get_member(user.id)
        if member is not None:
            if member.top_role.permissions.administrator:
                managing.append({'name': guild.name, 'id': str(guild.id)})
    return await render_template('guilds.html', guilds=json.dumps(managing))


@app.route("/settings/<int:guild_id>", methods=['GET', 'POST'])
async def settings(guild_id: int):
    if not await discordOAuth.authorized or not await verify_authorized(guild_id):
        return redirect(url_for('guilds'))

    if request.method == 'POST' and request.is_json:
        config.replace_settings_for_guild(guild_id, await request.json)

    sett = config.settings_for_guild_dict(guild_id)
    return await render_template('settings.html', settings=json.dumps(sett))


def init():
    webApp = threading.Thread(target=app.run).start()
    main()


if __name__ == "__main__":
    init()