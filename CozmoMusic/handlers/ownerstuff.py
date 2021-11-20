"""
MIT License
Copyright (C) 2021 Cozmo-Music
This file is part of https://github.com/VenujaBots/Cozmo-Music
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import os
import re
import math
import requests
import shutil
import sys
import heroku3
import traceback
import psutil
import subprocess
import socket
import platform
import uuid
import asyncio
import speedtest
from io import StringIO
from time import time
from functools import wraps
from os import environ, execle
from inspect import getfullargspec
from sys import version as pyver
from git import Repo
from pymongo import MongoClient
from git.exc import GitCommandError, InvalidGitRepositoryError
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from CozmoMusic.config import (
    HEROKU_API_KEY,
    HEROKU_APP_NAME,
    HEROKU_URL,
    U_BRANCH,
    UPSTREAM_REPO,
    OWNER_ID,
    BOT_NAME,
    DATABASE_URL,
    BOT_USERNAME,
)
from CozmoMusic.helpers.database import db
from CozmoMusic.helpers.dbtools import main_broadcast_handler
from CozmoMusic.handlers.song import get_text, humanbytes
from CozmoMusic.helpers.filters import command
from CozmoMusic.helpers.decorators import sudo_users_only


users_db = MongoClient(DATABASE_URL)['users']
col = users_db['USER']
grps = users_db['GROUPS']


# Stats Of Your Bot
"""
@Client.on_message(command("stats"))
@sudo_users_only
async def stats(_, message: Message):
    users = col.find({})
    mfs = []
    for x in users:
      mfs.append(x['user_id'])
    
    total = len(mfs)
  
    grp = grps.find({})
    grps_ = []
    for x in grp:
      grps_.append(x['chat_id'])
    
    total_ = len(grps_)
    totals, used, free = shutil.disk_usage(".")
    totals = humanbytes(total)
    used = humanbytes(used)
    free = humanbytes(free)
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage("/").percent
    total_users = await db.total_users_count()
    await message.reply_text(
        text=f"**📊 stats of [{BOT_NAME}](https://t.me/{BOT_USERNAME})** \n\n**💾 disk usage:** \n » **disk space:** `{totals}` \n » **used:** `{used}({disk_usage}%)` \n » **free:** `{free}` \n**🎛 hardware usage:** \n » **CPU usage:** `{cpu_usage}%` \n » **RAM usage:** `{ram_usage}%`\n» 👤 `{total}` users, across `{total_}` groups",
        disable_web_page_preview=True,
        parse_mode="Markdown",
        quote=True,
    )
"""

@Client.on_message(
    filters.private
    & filters.command("broadcast")
    & filters.user(OWNER_ID)
    & filters.reply
)
async def broadcast_handler_open(_, m: Message):
    await main_broadcast_handler(m, db)


@Client.on_message(filters.private & filters.command("block"))
@sudo_users_only
async def ban(c: Client, m: Message):
    if len(m.command) == 1:
        await m.reply_text(
            "» this command for ban user from using your bot, read /help for more info !",
            quote=True,
        )
        return
    try:
        user_id = int(m.command[1])
        ban_duration = m.command[2]
        ban_reason = " ".join(m.command[3:])
        ban_log_text = f"🚷 **banned user !** \n\nuser id: `{user_id}` \nduration: `{ban_duration}` \nreason: `{ban_reason}`"
        try:
            await c.send_message(
                user_id,
                f"😕 sorry, you're banned!** \n\nreason: `{ban_reason}` \nduration: `{ban_duration}` day(s). \n\n**💬 message from owner: ask in @{GROUP_SUPPORT} if you think this was an mistake.",
            )
            ban_log_text += "\n\n✅ this notification was sent to that user"
        except:
            traceback.print_exc()
            ban_log_text += f"\n\n❌ **failed sent this notification to that user** \n\n`{traceback.format_exc()}`"
        await db.ban_user(user_id, ban_duration, ban_reason)
        print(ban_log_text)
        await m.reply_text(ban_log_text, quote=True)
    except:
        traceback.print_exc()
        await m.reply_text(
            f"❌ an error occoured, traceback is given below:\n\n`{traceback.format_exc()}`",
            quote=True,
        )


# Unblock User
@Client.on_message(filters.private & filters.command("unblock"))
@sudo_users_only
async def unban(c: Client, m: Message):
    if len(m.command) == 1:
        await m.reply_text(
            "» this command for unban user, read /help for more info !", quote=True
        )
        return
    try:
        user_id = int(m.command[1])
        unban_log_text = f"🆓 **unbanned user !** \n\n**user id:**{user_id}"
        try:
            await c.send_message(user_id, "🎊 congratulations, you was unbanned!")
            unban_log_text += "\n\n✅ this notification was sent to that user"
        except:
            traceback.print_exc()
            unban_log_text += f"\n\n❌ **failed sent this notification to that user** \n\n`{traceback.format_exc()}`"
        await db.remove_ban(user_id)
        print(unban_log_text)
        await m.reply_text(unban_log_text, quote=True)
    except:
        traceback.print_exc()
        await m.reply_text(
            f"❌ an error occoured, traceback is given below:\n\n`{traceback.format_exc()}`",
            quote=True,
        )


# Blocked User List
@Client.on_message(filters.private & filters.command("blocklist"))
@sudo_users_only
async def _banned_usrs(_, m: Message):
    all_banned_users = await db.get_all_banned_users()
    banned_usr_count = 0
    text = ""
    async for banned_user in all_banned_users:
        user_id = banned_user["id"]
        ban_duration = banned_user["ban_status"]["ban_duration"]
        banned_on = banned_user["ban_status"]["banned_on"]
        ban_reason = banned_user["ban_status"]["ban_reason"]
        banned_usr_count += 1
        text += f"🆔 **user id**: `{user_id}`\n⏱ **duration**: `{ban_duration}`\n🗓 **banned date**: `{banned_on}`\n💬 **reason**: `{ban_reason}`\n\n"
    reply_text = f"🚷 **total banned:** `{banned_usr_count}`\n\n{text}"
    if len(reply_text) > 4096:
        with open("banned-user-list.txt", "w") as f:
            f.write(reply_text)
        await m.reply_document("banned-user-list.txt", True)
        os.remove("banned-user-list.txt")
        return
    await m.reply_text(reply_text, True)

# ====== UPDATER ======

REPO_ = UPSTREAM_REPO
BRANCH_ = U_BRANCH

async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {a}" for a in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)


async def edit_or_reply(msg: Message, **kwargs):
    func = msg.edit_text if msg.from_user.is_self else msg.reply
    spec = getfullargspec(func.__wrapped__).args
    await func(**{k: v for k, v in kwargs.items() if k in spec})


@Client.on_message(command("update") & filters.user(OWNER_ID))
async def updatebot(_, message: Message):
    msg = await message.reply_text("**updating bot, please wait for a while...**")
    try:
        repo = Repo()
    except GitCommandError:
        return await msg.edit("**invalid git command !**")
    except InvalidGitRepositoryError:
        repo = Repo.init()
        if "upstream" in repo.remotes:
            origin = repo.remote("upstream")
        else:
            origin = repo.create_remote("upstream", REPO_)
        origin.fetch()
        repo.create_head(U_BRANCH, origin.refs.main)
        repo.heads.main.set_tracking_branch(origin.refs.main)
        repo.heads.main.checkout(True)
    if repo.active_branch.name != U_BRANCH:
        return await msg.edit(f"**sorry, you are using costum branch named:** `{repo.active_branch.name}`!\n\nchange to `{U_BRANCH}` branch to continue update!")
    try:
        repo.create_remote("upstream", REPO_)
    except BaseException:
        pass
    ups_rem = repo.remote("upstream")
    ups_rem.fetch(U_BRANCH)
    if not HEROKU_URL:
        try:
            ups_rem.pull(U_BRANCH)
        except GitCommandError:
            repo.git.reset("--hard", "FETCH_HEAD")
        await run_cmd("pip3 install --no-cache-dir -r requirements.txt")
        await msg.edit("**update finished, restarting now...**")
        args = [sys.executable, "main.py"]
        execle(sys.executable, *args, environ)
        sys.exit()
        return
    else:
        await msg.edit("`heroku detected!`")
        await msg.edit("`updating and restarting is started, please wait for 5-10 minutes!`")
        ups_rem.fetch(U_BRANCH)
        repo.git.reset("--hard", "FETCH_HEAD")
        if "heroku" in repo.remotes:
            remote = repo.remote("heroku")
            remote.set_url(HEROKU_URL)
        else:
            remote = repo.create_remote("heroku", HEROKU_URL)
        try:
            remote.push(refspec="HEAD:refs/heads/main", force=True)
        except BaseException as error:
            await msg.edit(f"🚫 **updater error** \n\nTraceBack : `{error}`")
            return repo.__del__()


# HEROKU LOGS


async def edit_or_send_as_file(
    text: str,
    message: Message,
    client: Client,
    caption: str = "`Result!`",
    file_name: str = "result",
    parse_mode="md",
):
    """Send As File If Len Of Text Exceeds Tg Limit Else Edit Message"""
    if not text:
        await message.edit("`there is something other than text, aborting...`")
        return
    if len(text) <= 1024:
        return await message.edit(text, parse_mode=parse_mode)

    await message.edit("`output is too large, sending as file!`")
    file_names = f"{file_name}.text"
    open(file_names, "w").write(text)
    await client.send_document(message.chat.id, file_names, caption=caption)
    await message.delete()
    if os.path.exists(file_names):
        os.remove(file_names)
    return


heroku_client = heroku3.from_key(HEROKU_API_KEY) if HEROKU_API_KEY else None


def _check_heroku(func):
    @wraps(func)
    async def heroku_cli(client, message):
        heroku_app = None
        if not heroku_client:
            await message.reply_text("`Please Add Heroku API Key To Use This Feature!`")
        elif not HEROKU_APP_NAME:
            await edit_or_reply(message, "`Please Add Heroku APP Name To Use This Feature!`")
        if HEROKU_APP_NAME and heroku_client:
            try:
                heroku_app = heroku_client.app(HEROKU_APP_NAME)
            except:
                await message.reply_text(message, "`Heroku Api Key And App Name Doesn't Match! Check it again`")
            if heroku_app:
                await func(client, message, heroku_app)

    return heroku_cli


@Client.on_message(command("logs"))
@sudo_users_only
@_check_heroku
async def logswen(client: Client, message: Message, happ):
    msg = await message.reply_text("`please wait for a moment!`")
    logs = happ.get_log()
    capt = f"Heroku logs of `{HEROKU_APP_NAME}`"
    await edit_or_send_as_file(logs, msg, client, capt, "logs")


# Restart Bot
@Client.on_message(command("restart") & filters.user(OWNER_ID))
@_check_heroku
async def restart(client: Client, message: Message, hap):
    await message.reply_text("`restarting now, please wait...`")
    hap.restart()


# Set Heroku Var
@Client.on_message(command("setvar") & filters.user(OWNER_ID))
@_check_heroku
async def setvar(client: Client, message: Message, app_):
    msg = await message.reply_text("`please wait...`")
    heroku_var = app_.config()
    _var = get_text(message)
    if not _var:
        await msg.edit("**usage:** `/setvar (var) (value)`")
        return
    if " " not in _var:
        await msg.edit("**usage:** `/setvar (var) (value)`")
        return
    var_ = _var.split(" ", 1)
    if len(var_) > 2:
        await msg.edit("**usage:** `/setvar (var) (value)`")
        return
    _varname, _varvalue = var_
    await msg.edit(f"**variable:** `{_varname}` \n**new value:** `{_varvalue}`")
    heroku_var[_varname] = _varvalue


# Delete Heroku Var
@Client.on_message(command("delvar") & filters.user(OWNER_ID))
@_check_heroku
async def delvar(client: Client, message: Message, app_):
    msg = await message.reply_text("`please wait...!`")
    heroku_var = app_.config()
    _var = get_text(message)
    if not _var:
        await msg.edit("`give a var name to delete!`")
        return
    if _var not in heroku_var:
        await msg.edit("`this var doesn't exists!`")
        return
    await msg.edit(f"sucessfully deleted var `{_var}`")
    del heroku_var[_var]


# Modul From https://github.com/DevsExpo/Xtra-Plugins/blob/main/usage.py
# Port By https://github.com/FeriEXP | https://t.me/xflicks
# Usage Heroku Dyno


heroku_client = None
if HEROKU_API_KEY:
    heroku_client = heroku3.from_key(HEROKU_API_KEY)
    
def _check_heroku(func):
    @wraps(func)
    async def heroku_cli(client, message):
        if not heroku_client:
            await edit_or_reply(message, "`Please Add Heroku API Key For This To Function To Work!`")
        else:
            await func(client, message, heroku_client)
    return heroku_cli


def fetch_heroku_git_url(api_key, app_name):
    if not api_key:
        return None
    if not app_name:
        return None
    heroku = heroku3.from_key(api_key)
    try:
        heroku_applications = heroku.apps()
    except:
        return None
    heroku_app = None
    for app in heroku_applications:
        if app.name == app_name:
            heroku_app = app
            break
    if not heroku_app:
        return None
    return heroku_app.git_url.replace("https://", "https://api:" + api_key + "@")


@Client.on_message(command("usage"))
@sudo_users_only
@_check_heroku
async def gib_usage(client, message, hc):
  msg_ = await message.reply_text("`[HEROKU] - Please Wait.`")
  useragent = (
        "Mozilla/5.0 (Linux; Android 10; SM-G975F) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/80.0.3987.149 Mobile Safari/537.36"
    )
  acc_id = hc.account().id  
  headers = {
        "User-Agent": useragent,
        "Authorization": f"Bearer {HEROKU_API_KEY}",
        "Accept": "application/vnd.heroku+json; version=3.account-quotas",
    }
  heroku_api = "https://api.heroku.com"
  path = "/accounts/" + acc_id + "/actions/get-quota"
  r = requests.get(heroku_api + path, headers=headers)
  if r.status_code != 200:
        return await msg_.edit(f"`[{r.status_code}] - Something Isn't Right. Please Try Again Later.`")
  result = r.json()
  quota = result["account_quota"]
  quota_used = result["quota_used"]
  remaining_quota = quota - quota_used
  percentage = math.floor(remaining_quota / quota * 100)
  minutes_remaining = remaining_quota / 60
  hours = math.floor(minutes_remaining / 60)
  minutes = math.floor(minutes_remaining % 60)
  App = result["apps"]
  try:
      App[0]["quota_used"]
  except IndexError:
      AppQuotaUsed = 0
      AppPercentage = 0
  else:
      AppQuotaUsed = App[0]["quota_used"] / 60
      AppPercentage = math.floor(App[0]["quota_used"] * 100 / quota)
  AppHours = math.floor(AppQuotaUsed / 60)
  AppMinutes = math.floor(AppQuotaUsed % 60)
  app_name = HEROKU_APP_NAME or "Not Specified."
  return await msg_.edit(
        f"📅 <b>Dyno Usage {app_name}</b>\n\n"
        f"<b>✗ Usage in Hours And Minutes :</b>\n"
        f" • <code>{AppHours}h {AppMinutes}m</code>"
        f" | <code>[{AppPercentage} %]</code> \n\n"
        "<b>✗ Dyno Remaining This Months: </b>\n"
        f" • <code>{hours}h {minutes}m</code>"
        f" | <code>[{percentage}%]</code>",
    )


# eval and shell modules
# copyright VeezProject 2021
@Client.on_message(command("eval") & ~filters.edited)
@sudo_users_only
async def executor(client, message):
    if len(message.command) < 2:
        return await edit_or_reply(message, text="__please give me some command to execute.__")
    try:
        cmd = message.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await message.delete()
    t1 = time()
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    final_output = f"**OUTPUT**:\n\n```{evaluation.strip()}```"
    if len(final_output) > 4096:
        filename = "output.txt"
        with open(filename, "w+", encoding="utf8") as out_file:
            out_file.write(str(evaluation.strip()))
        t2 = time()
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="⏳", callback_data=f"runtime {t2-t1} Seconds"
                    )
                ]
            ]
        )
        await message.reply_document(
            document=filename,
            caption=f"**INPUT:**\n`{cmd[0:980]}`\n\n**OUTPUT:**\n`Attached Document`",
            quote=False,
            reply_markup=keyboard,
        )
        await message.delete()
        os.remove(filename)
    else:
        t2 = time()
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="⏳",
                        callback_data=f"runtime {round(t2-t1, 3)} Seconds",
                    )
                ]
            ]
        )
        await edit_or_reply(message, text=final_output, reply_markup=keyboard)


@Client.on_callback_query(filters.regex(r"runtime"))
async def runtime_func_cq(_, cq):
    runtime = cq.data.split(None, 1)[1]
    await cq.answer(runtime, show_alert=True)


@Client.on_message(command("sh") & ~filters.edited)
@sudo_users_only
async def shellrunner(client, message):
    if len(message.command) < 2:
        return await edit_or_reply(message, text="**usage:**\n\n/sh echo oni-chan")
    text = message.text.split(None, 1)[1]
    if "\n" in text:
        code = text.split("\n")
        output = ""
        for x in code:
            shell = re.split(""" (?=(?:[^'"]|'[^']*'|"[^"]*")*$)""", x)
            try:
                process = subprocess.Popen(
                    shell,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            except Exception as err:
                print(err)
                await edit_or_reply(message, text=f"**ERROR:**\n```{err}```")
            output += f"**{code}**\n"
            output += process.stdout.read()[:-1].decode("utf-8")
            output += "\n"
    else:
        shell = re.split(""" (?=(?:[^'"]|'[^']*'|"[^"]*")*$)""", text)
        for a in range(len(shell)):
            shell[a] = shell[a].replace('"', "")
        try:
            process = subprocess.Popen(
                shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as err:
            print(err)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            errors = traceback.format_exception(
                etype=exc_type,
                value=exc_obj,
                tb=exc_tb,
            )
            return await edit_or_reply(
                message, text=f"**ERROR:**\n\n```{''.join(errors)}```"
            )
        output = process.stdout.read()[:-1].decode("utf-8")
    if str(output) == "\n":
        output = None
    if output:
        if len(output) > 4096:
            with open("output.txt", "w+") as file:
                file.write(output)
            await app.send_document(
                message.chat.id,
                "output.txt",
                reply_to_message_id=message.message_id,
                caption="`Output`",
            )
            return os.remove("output.txt")
        await edit_or_reply(message, text=f"**OUTPUT:**\n\n```{output}```")
    else:
        await edit_or_reply(message, text="**OUTPUT: **\n`No output`")


@Client.on_message(command("sysinfo") & ~filters.edited)
@sudo_users_only
async def give_sysinfo(client, message):
    splatform = platform.system()
    platform_release = platform.release()
    platform_version = platform.version()
    architecture = platform.machine()
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(socket.gethostname())
    mac_address = ":".join(re.findall("..", "%012x" % uuid.getnode()))
    processor = platform.processor()
    ram = humanbytes(round(psutil.virtual_memory().total))
    cpu_freq = psutil.cpu_freq().current
    if cpu_freq >= 1000:
        cpu_freq = f"{round(cpu_freq / 1000, 2)}GHz"
    else:
        cpu_freq = f"{round(cpu_freq, 2)}MHz"
    du = psutil.disk_usage(client.workdir)
    psutil.disk_io_counters()
    disk = f"{humanbytes(du.used)} / {humanbytes(du.total)} " f"({du.percent}%)"
    cpu_len = len(psutil.Process().cpu_affinity())
    somsg = f"""**🖥 SYSTEM INFO**
    
**PlatForm :** `{splatform}`
**PlatForm - Release :** `{platform_release}`
**PlatFork - Version :** `{platform_version}`
**Architecture :** `{architecture}`
**Hostname :** `{hostname}`
**IP :** `{ip_address}`
**Mac :** `{mac_address}`
**Processor :** `{processor}`
**Ram : ** `{ram}`
**CPU :** `{cpu_len}`
**CPU FREQ :** `{cpu_freq}`
**DISK :** `{disk}`
    """
    await message.reply(somsg)


@Client.on_message(command("speedtest") & ~filters.edited)
@sudo_users_only
def speedtest_(_,message):
    speed = speedtest.Speedtest()
    speed.get_best_server()
    speed.download()
    speed.upload()
    speedtest_image = speed.results.share()

    message.reply_photo(speedtest_image)
