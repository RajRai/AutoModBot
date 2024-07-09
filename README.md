# Discord AutoModeration Bot (WIP)

This readme contains the basic information you need to work with the source. Each module is documented. Understanding the individual functions' behavior is for now left to you, since the project is very small and still being actively reworked on a lower level.

TODOs:
- Remove web UI, use slash commands
- Improve threading (if the web UI isn't removed)
- Better DB infrastructure
- Encrypt messages in DB
- There is probably a huge SQL injection vulnerability

I'm not going to be doing any of those things, as I have other things to work on, for now.

Everything below this might be outdated, it also might not.

## `main.py`
This is the main entry point to the bot, and its web interface. Both the Quart app and PyCord bot will be started asynchronously. The Quart app is dependent on the bot running, but the bot can be run independently of the Quart app.

In order to run the bot with this file, you'll need to place a file in the `config` folder named `private.py`, containing variables named `SECRET_KEY`, `CLIENT_ID`, `CLIENT_SECRET`, and `TOKEN`. 

To obtain the first three of these, see https://support.heateor.com/discord-client-id-discord-client-secret/. You will need to add a redirect URI when creating your application in the discord developer portal. That can be obtained from the `app.config["DISCORD_REDIRECT_URI"]` setting in `main.py`. `http://localhost:5000/callback` is the current redirect URI at the time of writing this.

To obtain a bot token (`TOKEN`), see https://www.writebots.com/discord-bot-token/. This should be done for the same Discord application you created previously.

Managing this private data for development and production branches is entirely your responsibility. Currently, the `private.py` is gitignored for security purposes. If you remove it from gitignore, make sure you're working in a private repo. 

*Anyone with the token can run an instance of the bot using their own code, with full permissions in every server your bot is a member of. Take care to make sure it's not exposed, or if it needs to be shared, carefully consider the risks of doing so given the circumstances.*

## `config`

### `config.py`
Contains configuration related data, and some helper functions which manage that data.

### `default_settings.json`
Contains the default settings that should be applied to new servers, before they access the web interface. Configure this as per your needs. If you don't want to run the web interface, this should contain the bot's base configuration in its entirety.


## `data`

Contains data, like the `settings.json` file and `.db` files.


## `src/bot`

The bot and its events (on message, on server join, etc.) are stored here (`bot.py`). Commands and permission-related functions for the commands are in `commands.py`. The `modules` directory contains the modules for lower-level handling of messages and configured filters/features. If you're unfamiliar with working with PyCord, see [the PyCord docs](https://docs.pycord.dev/en/master/index.html). The [api reference](https://docs.pycord.dev/en/master/api.html) is useful as well.

## `src/database`

Database related code, such as schema initialization, table cleanup, and query related code. `queries.py` is just for convenience. You can write SQL queries anywhere in the source.

## `static`

Static web files, like `.js` and `.css` go here. If you need to, read up on Flask.

## `templates`

Templated files, like `.html` files go here. Templated JavaScript can also go here, though I haven't figured out how to do it any way other than placing it in `<script>` tags, personally.

## Quart endpoints

The list of quart endpoints can be found in `main.py`. For now, `/` redirects to `/login`, which prompt the user to authorize via Discord. Authorization redirects them to `/guilds`, where a guild is chosen (provided they meet the permission requirements to modify bot settings in that guild), and they're sent to the settings page `/settings/<guild_id>`, which will present the settings page on a `GET` request, or take `POST`ed JSON data and load it into the bot's internally stored settings. The data represents *a single entry* in `settings.json`, keyed by the `guild_id` from the URL.
