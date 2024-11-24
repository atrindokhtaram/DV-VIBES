#
# Copyright (C) 2024 by IamDvis@Github, < https://github.com/IamDvis >.
#
# This file is part of < https://github.com/IamDvis/DV-VIBES > project,
# and is released under the MIT License.
# Please see < https://github.com/IamDvis/DV-VIBES/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
import time

from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message, ChatPermissions
from pyrogram.raw import functions, types
from pyrogram.errors import UserNotParticipant


from ANWIVIBES import app
from ANWIVIBES.utils import get_readable_time
from ANWIVIBES.utils.database import (
    add_banned_user,
    get_banned_count,
    get_banned_users,
    get_served_chats,
    is_banned_user,
    remove_banned_user,
)
from ANWIVIBES.utils.decorators.language import language
from ANWIVIBES.utils.extraction import extract_user
from config import BANNED_USERS, OWNER_ID

app = Client("voice_call_manager")
# دیکشنری برای ذخیره اطلاعات ویس کال‌ها
voice_calls = {}

def is_admin(user_id: int) -> bool:
    """بررسی ادمین بودن کاربر"""
    return user_id in ADMIN_LIST

@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    """دستور شروع"""
    await message.reply_text(
        "👋 سلام! من ربات مدیریت ویس کال هستم.\n"
        "دستورات موجود:\n"
        "/startvc - شروع ویس کال\n"
        "/endvc - پایان ویس کال\n"
        "/mu - سکوت کاربر\n"
        "/unmute - لغو سکوت کاربر\n"
        "/mutelist - لیست کاربران ساکت شده\n"
        "/kick - اخراج کاربر از ویس کال\n"
        "/info - اطلاعات ویس کال فعلی"
    )

@app.on_message(filters.command("startvc"))
async def start_voice_call(client, message: Message):
    """شروع ویس کال"""
    if not is_admin(message.from_user.id):
        await message.reply_text("❌ شما دسترسی به این دستور را ندارید!")
        return

    chat_id = message.chat.id
    
    try:
        # شروع ویس کال
        voice_call = await client.invoke(
            functions.phone.CreateGroupCall(
                peer=await client.resolve_peer(chat_id),
                random_id=int(time.time())
            )
        )
        
        # ذخیره اطلاعات ویس کال
        voice_calls[chat_id] = {
            "id": voice_call.updates[0].call.id,
            "muted_users": set(),
            "start_time": time.time()
        }
        
        await message.reply_text("✅ ویس کال با موفقیت شروع شد!")
    
    except Exception as e:
        await message.reply_text(f"❌ خطا در شروع ویس کال: {str(e)}")

@app.on_message(filters.command("endvc"))
async def end_voice_call(client, message: Message):
    """پایان ویس کال"""
    if not is_admin(message.from_user.id):
        await message.reply_text("❌ شما دسترسی به این دستور را ندارید!")
        return

    chat_id = message.chat.id
    
    if chat_id not in voice_calls:
        await message.reply_text("❌ ویس کال فعالی وجود ندارد!")
        return
    
    try:
        # پایان ویس کال
        await client.invoke(
            functions.phone.DiscardGroupCall(
                call=types.InputGroupCall(
                    id=voice_calls[chat_id]["id"],
                    access_hash=0
                )
            )
        )
        
        del voice_calls[chat_id]
        await message.reply_text("✅ ویس کال با موفقیت پایان یافت!")
    
    except Exception as e:
        await message.reply_text(f"❌ خطا در پایان ویس کال: {str(e)}")

@app.on_message(filters.command("mu"))
async def mute_user(client, message: Message):
    """سکوت کردن کاربر"""
    if not is_admin(message.from_user.id):
        await message.reply_text("❌ شما دسترسی به این دستور را ندارید!")
        return

    if len(message.command) < 2:
        await message.reply_text("❌ لطفاً نام کاربری یا آیدی کاربر را وارد کنید!")
        return

    chat_id = message.chat.id
    if chat_id not in voice_calls:
        await message.reply_text("❌ ویس کال فعالی وجود ندارد!")
        return

    try:
        # دریافت اطلاعات کاربر
        user = await client.get_users(message.command[1])
        
        # اعمال سکوت
        await client.invoke(
            functions.phone.EditGroupCallParticipant(
                call=types.InputGroupCall(
                    id=voice_calls[chat_id]["id"],
                    access_hash=0
                ),
                participant=await client.resolve_peer(user.id),
                muted=True
            )
        )
        
        voice_calls[chat_id]["muted_users"].add(user.id)
        await message.reply_text(f"✅ کاربر {user.first_name} ساکت شد!")
    
    except Exception as e:
        await message.reply_text(f"❌ خطا در سکوت کردن کاربر: {str(e)}")

@app.on_message(filters.command("unmute"))
async def unmute_user(client, message: Message):
    """لغو سکوت کاربر"""
    if not is_admin(message.from_user.id):
        await message.reply_text("❌ شما دسترسی به این دستور را ندارید!")
        return

    if len(message.command) < 2:
        await message.reply_text("❌ لطفاً نام کاربری یا آیدی کاربر را وارد کنید!")
        return

    chat_id = message.chat.id
    if chat_id not in voice_calls:
        await message.reply_text("❌ ویس کال فعالی وجود ندارد!")
        return

    try:
        # دریافت اطلاعات کاربر
        user = await client.get_users(message.command[1])
        
        # لغو سکوت
        await client.invoke(
            functions.phone.EditGroupCallParticipant(
                call=types.InputGroupCall(
                    id=voice_calls[chat_id]["id"],
                    access_hash=0
                ),
                participant=await client.resolve_peer(user.id),
                muted=False
            )
        )
        
        voice_calls[chat_id]["muted_users"].discard(user.id)
        await message.reply_text(f"✅ سکوت کاربر {user.first_name} لغو شد!")
    
    except Exception as e:
        await message.reply_text(f"❌ خطا در لغو سکوت کاربر: {str(e)}")

@app.on_message(filters.command("mutelist"))
async def muted_list(client, message: Message):
    """نمایش لیست کاربران ساکت شده"""
    if not is_admin(message.from_user.id):
        await message.reply_text("❌ شما دسترسی به این دستور را ندارید!")
        return

    chat_id = message.chat.id
    if chat_id not in voice_calls:
        await message.reply_text("❌ ویس کال فعالی وجود ندارد!")
        return

    if not voice_calls[chat_id]["muted_users"]:
        await message.reply_text("📝 لیست کاربران ساکت شده خالی است!")
        return

    muted_list = "📝 لیست کاربران ساکت شده:\n\n"
    for user_id in voice_calls[chat_id]["muted_users"]:
        try:
            user = await client.get_users(user_id)
            muted_list += f"- {user.first_name} (@{user.username})\n"
        except:
            continue

    await message.reply_text(muted_list)

@app.on_message(filters.command("kick"))
async def kick_user(client, message: Message):
    """اخراج کاربر از ویس کال"""
    if not is_admin(message.from_user.id):
        await message.reply_text("❌ شما دسترسی به این دستور را ندارید!")
        return

    if len(message.command) < 2:
        await message.reply_text("❌ لطفاً نام کاربری یا آیدی کاربر را وارد کنید!")
        return

    chat_id = message.chat.id
    if chat_id not in voice_calls:
        await message.reply_text("❌ ویس کال فعالی وجود ندارد!")
        return

    try:
        # دریافت اطلاعات کاربر
        user = await client.get_users(message.command[1])
        
        # اخراج کاربر
        await client.invoke(
            functions.phone.EditGroupCallParticipant(
                call=types.InputGroupCall(
                    id=voice_calls[chat_id]["id"],
                    access_hash=0
                ),
                participant=await client.resolve_peer(user.id),
                kicked=True
            )
        )
        
        await message.reply_text(f"✅ کاربر {user.first_name} از ویس کال اخراج شد!")
    
    except Exception as e:
        await message.reply_text(f"❌ خطا در اخراج کاربر: {str(e)}")

@app.on_message(filters.command("info"))
async def voice_call_info(client, message: Message):
    """نمایش اطلاعات ویس کال"""
    chat_id = message.chat.id
    if chat_id not in voice_calls:
        await message.reply_text("❌ ویس کال فعالی وجود ندارد!")
        return

    duration = int(time.time() - voice_calls[chat_id]["start_time"])
    hours = duration // 3600
    minutes = (duration % 3600) // 60
    seconds = duration % 60

    info = (
        "📊 اطلاعات ویس کال:\n\n"
        f"⏱ مدت زمان: {hours:02d}:{minutes:02d}:{seconds:02d}\n"
        f"👥 تعداد کاربران ساکت شده: {len(voice_calls[chat_id]['muted_users'])}"
    )

    await message.reply_text(info)

# اجرای ربات
print("🤖 ربات در حال اجرا است...")

@app.on_message(filters.command(["gban", "globalban"]) & OWNER_ID)
@language
async def global_ban(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])
    user = await extract_user(message)
    if user.id == message.from_user.id:
        return await message.reply_text(_["gban_1"])
    elif user.id == app.id:
        return await message.reply_text(_["gban_2"])
    elif user.id in OWNER_ID:
        return await message.reply_text(_["gban_3"])
    is_gbanned = await is_banned_user(user.id)
    if is_gbanned:
        return await message.reply_text(_["gban_4"].format(user.mention))
    if user.id not in BANNED_USERS:
        BANNED_USERS.add(user.id)
    served_chats = []
    chats = await get_served_chats()
    for chat in chats:
        served_chats.append(int(chat["chat_id"]))
    time_expected = get_readable_time(len(served_chats))
    mystic = await message.reply_text(_["gban_5"].format(user.mention, time_expected))
    number_of_chats = 0
    for chat_id in served_chats:
        try:
            await app.ban_chat_member(chat_id, user.id)
            number_of_chats += 1
        except FloodWait as fw:
            await asyncio.sleep(int(fw.value))
        except:
            continue
    await add_banned_user(user.id)
    await message.reply_text(
        _["gban_6"].format(
            app.mention,
            message.chat.title,
            message.chat.id,
            user.mention,
            user.id,
            message.from_user.mention,
            number_of_chats,
        )
    )
    await mystic.delete()


@app.on_message(filters.command(["ungban"]) & OWNER_ID)
@language
async def global_un(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])
    user = await extract_user(message)
    is_gbanned = await is_banned_user(user.id)
    if not is_gbanned:
        return await message.reply_text(_["gban_7"].format(user.mention))
    if user.id in BANNED_USERS:
        BANNED_USERS.remove(user.id)
    served_chats = []
    chats = await get_served_chats()
    for chat in chats:
        served_chats.append(int(chat["chat_id"]))
    time_expected = get_readable_time(len(served_chats))
    mystic = await message.reply_text(_["gban_8"].format(user.mention, time_expected))
    number_of_chats = 0
    for chat_id in served_chats:
        try:
            await app.unban_chat_member(chat_id, user.id)
            number_of_chats += 1
        except FloodWait as fw:
            await asyncio.sleep(int(fw.value))
        except:
            continue
    await remove_banned_user(user.id)
    await message.reply_text(_["gban_9"].format(user.mention, number_of_chats))
    await mystic.delete()


@app.on_message(filters.command(["gbannedusers", "gbanlist"]) & OWNER_ID)
@language
async def gbanned_list(client, message: Message, _):
    counts = await get_banned_count()
    if counts == 0:
        return await message.reply_text(_["gban_10"])
    mystic = await message.reply_text(_["gban_11"])
    msg = _["gban_12"]
    count = 0
    users = await get_banned_users()
    for user_id in users:
        count += 1
        try:
            user = await app.get_users(user_id)
            user = user.first_name if not user.mention else user.mention
            msg += f"❖ {count} ➥ {user}\n"
        except Exception:
            msg += f"❖ {count} ➥ {user_id}\n"
            continue
    if count == 0:
        return await mystic.edit_text(_["gban_10"])
    else:
        return await mystic.edit_text(msg)
