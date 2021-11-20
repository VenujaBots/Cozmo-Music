import os
from os import getenv
from dotenv import load_dotenv
from CozmoMusic.helpers.uptools import fetch_heroku_git_url

if os.path.exists("local.env"):
    load_dotenv("local.env")

load_dotenv()
que = {}
admins = {}
SESSION_NAME = getenv("SESSION_NAME", "BQDAKzBlrhax1hUfIY-n1m-aYCoFkTgHWbK200jqFxHghw2DAGIA4X-ZpDDTSANrUBVq3_Kcq4gfW6jbh4d1MAtKZ-76lmSnBH7H3bNe_XIGaZw6FxtujuXx8eZu6G5L9wRMHOiUKMMihsmZHil1cWUzf6AWESy_z-imf4sYjX94dCWivL4bxvLk1zIW__1iPxSMtA-k82GPgCpjgj6K3L2SSmXV1sAOCYQW3dmmliHfcjcuLECo8Cwfb4gGgL4px5LqLEiUkSwnettG8BMldgEym6zsPihJaabArwDIauhRi2laNY1Lhi-gDNUUmLiW8-ZdgeHCJIk697hUsOd32djqdkfIGgA")
BOT_TOKEN = getenv("2125818764:AAG69T8jz0qNI_BaOnjRwDr0dUhRIHC7HXE")
BOT_NAME = getenv("BOT_NAME", "Cozmo Music Bot")
THUMB_IMG = getenv("THUMB_IMG", "https://telegra.ph/file/485ab26296b36b924e75b.jpg")
BG_IMAGE = getenv("BG_IMAGE", "https://telegra.ph/file/017de119883a2dac16264.png")
BOT_IMG = getenv("BOT_IMG", "https://telegra.ph/file/2ca0f8f64645406f43ff1.jpg")
API_ID = int(getenv("18862638"))
API_HASH = getenv("2a4a8dc0c1f6c9cb65f9f144439558ae")
BOT_USERNAME = getenv("BOT_USERNAME", "CozmoMusicBot")
ASSISTANT_NAME = getenv("ASSISTANT_NAME", "CozmoMusicHelper")
GROUP_SUPPORT = getenv("GROUP_SUPPORT", "CozmoBotSupport")
UPDATES_CHANNEL = getenv("UPDATES_CHANNEL", "CozmoMusicProject")
OWNER_NAME = getenv("OWNER_NAME", "Venuja_Sadew") # fill in your username without the @ symbol
ALIVE_EMOJI = getenv("ALIVE_EMOJI", "⚪")
PMPERMIT = getenv("PMPERMIT", "ENABLE")
DURATION_LIMIT = int(getenv("DURATION_LIMIT", "60"))
COMMAND_PREFIXES = list(getenv("COMMAND_PREFIXES", "/ ! .").split())
SUDO_USERS = list(map(int, getenv("1984415770").split()))
OWNER_ID = int(os.environ.get("1984415770"))
# Database
DATABASE_URL = os.environ.get("mongodb+srv://CozmoBot:CozmoBot@cluster0.qo4iu.mongodb.net/cluster0?retryWrites=true&w=majority")  # fill with your mongodb url
# make a private channel and get the channel id
LOG_CHANNEL = int(os.environ.get("-1001671628818"))
# just fill with True or False (optional)
BROADCAST_AS_COPY = bool(os.environ.get("BROADCAST_AS_COPY", "True"))
# UPDATER CONFIG
U_BRANCH = "main"
HEROKU_APP_NAME = os.environ.get("cozmomusic", None)
HEROKU_API_KEY = os.environ.get("23e77761-7108-40dc-9301-f1efec0f182b", None)
UPSTREAM_REPO = os.environ.get("UPSTREAM_REPO", "https://github.com/VenujaBots/Cozmo-Music")
HEROKU_URL = fetch_heroku_git_url(HEROKU_API_KEY, HEROKU_APP_NAME)
