from asyncio import QueueEmpty

from CozmoMusic.callsmusic import callsmusic
from CozmoMusic.callsmusic.queues import queues
from CozmoMusic.config import BOT_USERNAME, que
from CozmoMusic.cache.admins import admins
from CozmoMusic.handlers.play import cb_admin_check
from CozmoMusic.helpers.channelmusic import get_chat_id
from CozmoMusic.helpers.dbtools import delcmd_is_on, delcmd_off, delcmd_on
from CozmoMusic.helpers.decorators import authorized_users_only, errors
from CozmoMusic.helpers.filters import command, other_filters
from pyrogram import Client, filters
from pytgcalls.types.input_stream import InputStream, InputAudioStream
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

@Client.on_message(command(["reload", f"reload@{BOT_USERNAME}"]))
@authorized_users_only
async def update_admin(client, message):
    global admins
    new_admins = []
    new_ads = await client.get_chat_members(message.chat.id, filter="administrators")
    for u in new_ads:
        new_admins.append(u.user.id)
    admins[message.chat.id] = new_admins
    await client.send_message(message.chat.id, "✅ Bot **reloaded correctly!**\n\n• The **Admin list** has been **updated.**")


@Client.on_message(command(["pause", f"pause@{BOT_USERNAME}"]) & other_filters)
@errors
@authorized_users_only
async def pause(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if chat_id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("❌ **no music is currently playing**")
    else:
        await callsmusic.pytgcalls.pause_stream(chat_id)
        await _.send_message(message.chat.id, "▶️ **Music paused!**\n\n• To resume the music playback, use **command » /resume**")


@Client.on_message(command(["resume", f"resume@{BOT_USERNAME}"]) & other_filters)
@errors
@authorized_users_only
async def resume(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if chat_id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("❌ **no music is paused**")
    else:
        await callsmusic.pytgcalls.resume_stream(chat_id)
        await _.send_message(message.chat.id, "⏸ **Music resumed!**\n\n• To pause the music playback, use **command » /pause**")


@Client.on_message(command(["end", f"end@{BOT_USERNAME}"]) & other_filters)
@errors
@authorized_users_only
async def stop(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if chat_id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("❌ **no music is currently playing**")
    else:
        try:
            queues.clear(chat_id)
        except QueueEmpty:
            pass
        await remove_active_chat(chat_id)            
        await callsmusic.pytgcalls.leave_group_call(chat_id)
        await _.send_message(message.chat.id, "✅ __The Userbot has disconnected from voice chat__")


@Client.on_message(command("skip") & other_filters)
@errors
@authorized_users_only
async def skip(_, message: Message):
    global que
    chat_id = get_chat_id(message.chat)
    if chat_id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("❌ **no music is currently playing**")
    else:
        queues.task_done(chat_id)
            
        if queues.is_empty(chat_id):
            await remove_active_chat(chat_id)
            await callsmusic.pytgcalls.leave_group_call(chat_id)
            await _.send_message(message.chat.id, "❌ __No more music in Queues, Leaving voice chats__") 
        else:
            await callsmusic.pytgcalls.change_stream(
                chat_id,
                InputStream(
                    InputAudioStream(
                        callsmusic.queues.get(chat_id)["file"],
                    ),
                ),
            )
                
    qeue = que.get(chat_id)
    if qeue:
        qeue.pop(0)
    if not qeue:
        return
    await _.send_message(message.chat.id, f"⏭️ __You've skipped to the next song__")


@Client.on_message(command(["auth", f"auth@{BOT_USERNAME}"]) & other_filters)
@authorized_users_only
async def authenticate(client, message):
    global admins
    if not message.reply_to_message:
        return await message.reply("🔔 reply to message to authorize user !")
    if message.reply_to_message.from_user.id not in admins[message.chat.id]:
        new_admins = admins[message.chat.id]
        new_admins.append(message.reply_to_message.from_user.id)
        admins[message.chat.id] = new_admins
        await message.reply(
            "👮 user authorized.\n\nfrom now on, that's user can use the admin commands."
        )
    else:
        await message.reply("✅ user already authorized!")


@Client.on_message(command(["unauth", f"deauth@{BOT_USERNAME}"]) & other_filters)
@authorized_users_only
async def deautenticate(client, message):
    global admins
    if not message.reply_to_message:
        return await message.reply("🔔 reply to message to deauthorize user !")
    if message.reply_to_message.from_user.id in admins[message.chat.id]:
        new_admins = admins[message.chat.id]
        new_admins.remove(message.reply_to_message.from_user.id)
        admins[message.chat.id] = new_admins
        await message.reply(
            "👷 user deauthorized.\n\nfrom now that's user can't use the admin commands."
        )
    else:
        await message.reply("✅ user already deauthorized!")


@Client.on_message(command(["delcmd", f"delcmd@{BOT_USERNAME}"]) & other_filters)
@authorized_users_only
async def delcmdc(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text(
            "read the **⚙️ help** message to know how to use this command"
        )
    status = message.text.split(None, 1)[1].strip()
    status = status.lower()
    chat_id = message.chat.id
    if status == "on":
        if await delcmd_is_on(message.chat.id):
            return await message.reply_text("✅ already activated")
        await delcmd_on(chat_id)
        await message.reply_text("🟢 activated successfully")
    elif status == "off":
        await delcmd_off(chat_id)
        await message.reply_text("🔴 disabled successfully")
    else:
        await message.reply_text(
            "read the **⚙️ help** message to know how to use this command"
        )
