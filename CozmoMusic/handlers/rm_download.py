# function to remove the downloaded files

import os
from pyrogram import Client, filters
from pyrogram.types import Message
from CozmoMusic.helpers.filters import command
from CozmoMusic.helpers.decorators import sudo_users_only, errors

downloads = os.path.realpath("downloads")
raw = os.path.realpath("raw_files")

@Client.on_message(command(["rmd", "rmdownload"]) & ~filters.edited)
@errors
@sudo_users_only
async def clear_downloads(_, message: Message):
    ls_dir = os.listdir(downloads)
    if ls_dir:
        for file in os.listdir(downloads):
            os.remove(os.path.join(downloads, file))
        await message.reply_text("🗑️ **Delete all downloaded files**")
    else:
        await message.reply_text("❌ **The downloaded file is empty, just like your heart!**")
