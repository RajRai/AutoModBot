from quart_discord import DiscordOAuth2Session
from src.bot import main
from quart import Quart, render_template, request, session, redirect, url_for
from src.private import SECRET_KEY, CLIENT_ID, CLIENT_SECRET


app = Quart(__name__)

app.config["SECRET_KEY"] = SECRET_KEY
app.config["DISCORD_CLIENT_ID"] = CLIENT_ID  # Discord client ID.
app.config["DISCORD_CLIENT_SECRET"] = CLIENT_SECRET  # Discord client secret.
app.config["DISCORD_REDIRECT_URI"] = "http://github.com"
discordOAuth = DiscordOAuth2Session(app)

@app.route("/login")
async def login():
    return await discordOAuth.create_session()

if __name__ == "__main__":
    main()