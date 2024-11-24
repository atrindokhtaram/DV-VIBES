from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import os
from pydub import AudioSegment
import asyncio


# ایجاد نمونه ربات
app = Client("music_volume_bot")

# دیکشنری برای ذخیره تنظیمات صدا برای هر کاربر
user_volumes = {}

# دکمه‌های تنظیم صدا
volume_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🔈 کم", callback_data="volume_down"),
        InlineKeyboardButton("🔊 زیاد", callback_data="volume_up")
    ],
    [InlineKeyboardButton("✅ تایید", callback_data="volume_confirm")]
])

@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    """دستور شروع"""
    await message.reply_text(
        "👋 سلام! من ربات تنظیم صدای موزیک هستم.\n"
        "برای تنظیم صدای یک فایل صوتی، آن را برای من ارسال کنید."
    )

@app.on_message(filters.audio | filters.voice)
async def handle_audio(client, message: Message):
    """پردازش فایل صوتی"""
    try:
        # دریافت فایل
        audio_file = await message.download()
        user_id = message.from_user.id
        
        # ذخیره مسیر فایل و تنظیم صدای پیش‌فرض
        user_volumes[user_id] = {
            "file_path": audio_file,
            "volume": 1.0
        }
        
        await message.reply_text(
            "🎵 لطفاً میزان صدای مورد نظر را انتخاب کنید:",
            reply_markup=volume_keyboard
        )
    
    except Exception as e:
        await message.reply_text(f"❌ خطا در پردازش فایل: {str(e)}")

@app.on_callback_query()
async def volume_callback(client, callback_query):
    """پردازش دکمه‌های تنظیم صدا"""
    user_id = callback_query.from_user.id
    
    if user_id not in user_volumes:
        await callback_query.answer("❌ لطفاً ابتدا یک فایل صوتی ارسال کنید.")
        return

    data = callback_query.data
    current_volume = user_volumes[user_id]["volume"]
    
    if data == "volume_up":
        # افزایش صدا
        new_volume = min(current_volume + 0.2, 2.0)
        user_volumes[user_id]["volume"] = new_volume
        await callback_query.answer(f"🔊 صدا: {new_volume:.1f}x")
        
    elif data == "volume_down":
        # کاهش صدا
        new_volume = max(current_volume - 0.2, 0.2)
        user_volumes[user_id]["volume"] = new_volume
        await callback_query.answer(f"🔈 صدا: {new_volume:.1f}x")
        
    elif data == "volume_confirm":
        await process_audio(client, callback_query, user_id)

async def process_audio(client, callback_query, user_id):
    """پردازش نهایی فایل صوتی"""
    try:
        # نمایش پیام در حال پردازش
        processing_message = await callback_query.message.edit_text(
            "⏳ در حال پردازش فایل صوتی..."
        )
        
        # دریافت اطلاعات فایل
        file_path = user_volumes[user_id]["file_path"]
        volume = user_volumes[user_id]["volume"]
        
        # تغییر صدای فایل
        audio = AudioSegment.from_file(file_path)
        audio = audio + (20 * log10(volume))  # تبدیل به دسیبل
        
        # ذخیره فایل جدید
        output_path = f"output_{user_id}.mp3"
        audio.export(output_path, format="mp3")
        
        # ارسال فایل جدید
        await client.send_audio(
            callback_query.message.chat.id,
            output_path,
            caption=f"🎵 فایل صوتی با تنظیم صدای {volume:.1f}x"
        )
        
        # پاکسازی فایل‌ها
        os.remove(file_path)
        os.remove(output_path)
        del user_volumes[user_id]
        
        await processing_message.delete()
        
    except Exception as e:
        await callback_query.message.reply_text(f"❌ خطا در پردازش: {str(e)}")
        if user_id in user_volumes:
            del user_volumes[user_id]

# تابع کمکی برای محاسبه لگاریتم
from math import log10

print("🤖 ربات در حال اجرا است...")
app.run()
