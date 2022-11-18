import aiohttp
from config import settings
from pyrogram import Client

api_id = settings.api_id
api_hash = settings.api_hash
bot_token = settings.bot_token

plugins = dict(
    root="plugins",
)


# session = aiohttp.ClientSession()


app = Client(
    "TelegramYoutubeBot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token,
    in_memory=True,
    plugins=plugins,
)

app.run()
