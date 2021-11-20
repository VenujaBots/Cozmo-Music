import datetime
from typing import Dict, List, Union
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

from CozmoMusic.config import DATABASE_URL

MONGODB_CLI = MongoClient(DATABASE_URL)
db = MONGODB_CLI.wbb
dcmdb = db.handlers
restart_stagedb = db.restart_stage
pytgdb = db.pytg
admindb = db.admin


class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    def new_user(self, id):
        return dict(
            id=id,
            join_date=datetime.date.today().isoformat(),
            ban_status=dict(
                is_banned=False,
                ban_duration=0,
                banned_on=datetime.date.max.isoformat(),
                ban_reason="",
            ),
        )

    async def add_user(self, id):
        user = self.new_user(id)
        await self.col.insert_one(user)

    async def is_user_exist(self, id):
        user = await self.col.find_one({"id": int(id)})
        return bool(user)

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({"id": int(user_id)})

    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_duration=0,
            banned_on=datetime.date.max.isoformat(),
            ban_reason="",
        )
        await self.col.update_one({"id": id}, {"$set": {"ban_status": ban_status}})

    async def ban_user(self, user_id, ban_duration, ban_reason):
        ban_status = dict(
            is_banned=True,
            ban_duration=ban_duration,
            banned_on=datetime.date.today().isoformat(),
            ban_reason=ban_reason,
        )
        await self.col.update_one({"id": user_id}, {"$set": {"ban_status": ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_duration=0,
            banned_on=datetime.date.max.isoformat(),
            ban_reason="",
        )
        user = await self.col.find_one({"id": int(id)})
        return user.get("ban_status", default)

    async def get_all_banned_users(self):
        return self.col.find({"ban_status.is_banned": True})


async def start_restart_stage(chat_id: int, message_id: int):
    await restart_stagedb.update_one(
        {"something": "something"},
        {
            "$set": {
                "chat_id": chat_id,
                "message_id": message_id,
            }
        },
        upsert=True,
    )


async def clean_restart_stage() -> dict:
    data = await restart_stagedb.find_one({"something": "something"})
    if not data:
        return {}
    await restart_stagedb.delete_one({"something": "something"})
    return {"chat_id": data["chat_id"], "message_id": data["message_id"]}


## Queue Chats

async def get_active_chats() -> list:
    chats = pytgdb.find({"chat_id": {"$lt": 0}})
    if not chats:
        return []
    chats_list = []
    for chat in await chats.to_list(length=1000000000):
        chats_list.append(chat)
    return chats_list
    
async def is_active_chat(chat_id: int) -> bool:
    chat = await pytgdb.find_one({"chat_id": chat_id})
    if not chat:
        return False
    return True

async def add_active_chat(chat_id: int):
    is_served = await is_active_chat(chat_id)
    if is_served:
        return
    return await pytgdb.insert_one({"chat_id": chat_id})

async def remove_active_chat(chat_id: int):
    is_served = await is_active_chat(chat_id)
    if not is_served:
        return
    return await pytgdb.delete_one({"chat_id": chat_id})

  
## Music Playing or Paused  
    
async def is_music_playing(chat_id: int) -> bool:
    chat = await admindb.find_one({"chat_id_toggle": chat_id})
    if not chat:
        return True
    return False

async def music_on(chat_id: int):
    dis_kontol = await is_music_playing(chat_id)
    if dis_kontol:
        return
    return await admindb.delete_one({"chat_id_toggle": chat_id})

async def music_off(chat_id: int):
    dis_kontol = await is_music_playing(chat_id)
    if not dis_kontol:
        return
    return await admindb.insert_one({"chat_id_toggle": chat_id})
