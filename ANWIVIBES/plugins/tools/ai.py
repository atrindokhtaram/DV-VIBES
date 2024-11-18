import os
import tempfile
import requests
from gtts import gTTS
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from ANWIVIBES import app

@app.on_message(filters.command("siri"))
async def chat_annie(app, message):
    try:
        await app.send_chat_action(message.chat.id, ChatAction.TYPING)
        name = message.from_user.first_name

        if len(message.command) < 2:
            await message.reply_text(f"Hello {name}, I am Siri. How can I help you today?")
            return

        query = message.text.split(' ', 1)[1]

        # Send query as a parameter in the URL
        try:
            response = requests.post(f"https://chatwithai.codesearch.workers.dev/?chat={query}", timeout=10)

            if response.status_code == 200:
                response_data = response.json()
                response_text = response_data.get("response", "I couldn't understand that.")
            else:
                await message.reply_text(f"API Error: {response.status_code} - {response.text}")
                return

        except requests.exceptions.RequestException as e:
            await message.reply_text(f"API Request Failed: {str(e)}")
            return

        # Convert response text to speech (default language: English)
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                tts = gTTS(response_text, lang="en")  # Default language set to English
                tts.save(temp_file.name)
                await app.send_voice(chat_id=message.chat.id, voice=temp_file.name)
        finally:
            os.remove(temp_file.name)

    except Exception as e:
        await message.reply_text(f"An unexpected error occurred: {str(e)}")
