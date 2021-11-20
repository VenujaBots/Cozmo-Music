import logging
from pyrogram.types import Message
from youtube_search import YoutubeSearch
from pyrogram import Client as app
from CozmoMusic.helpers.filters import command
from CozmoMusic.config import BOT_USERNAME


logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


@app.on_message(command(["search", f"search@{BOT_USERNAME}"]))
async def ytsearch(_, message: Message):
    try:
        if len(message.command) < 2:
            await message.reply_text("/search needs an argument!")
            return
        query = message.text.split(None, 1)[1]
        m = await message.reply_text("🔎 **searching**")
        results = YoutubeSearch(query, max_results=5).to_dict()
        i = 0
        text = ""
        while i < 5:
            text += f"🏷️ **Judul:** `{results[i]['title']}`\n"
            text += f"⏱️ **Durasi:** {results[i]['duration']}\n"
            text += f"👁️‍🗨️ **Views:** {results[i]['views']}\n"
            text += f"💡 **Channel:** {results[i]['channel']}\n"
            text += f"🖇️ https://www.youtube.com{results[i]['url_suffix']}\n\n"
            i += 1
        await m.edit(text, disable_web_page_preview=True)
    except Exception as e:
        await m.edit(str(e))
