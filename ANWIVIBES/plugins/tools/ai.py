import os
import tempfile
import requests  # To make API requests
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
        
        # Prepare the API payload
        payload = {
            "model": "chatgpt-4",  # Specify the model
            "input": query        # User's query
        }

        # Make the API request directly with the URL
        response = requests.post("https://chatwithai.codesearch.workers.dev/?chat=", json=payload)
        
        if response.status_code == 200:
            response_data = response.json()
            response_text = response_data.get("response", "I couldn't understand that.")
        else:
            await message.reply_text("Sorry, I couldn't process your request. Please try again later.")
            return

        # Convert text to speech
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                tts = gTTS(response_text, lang='en')
                tts.save(temp_file.name)
                await app.send_voice(chat_id=message.chat.id, voice=temp_file.name)
        finally:
            os.remove(temp_file.name)

    except Exception as e:
        await message.reply_text(f"An unexpected error occurred: {str(e)}")
