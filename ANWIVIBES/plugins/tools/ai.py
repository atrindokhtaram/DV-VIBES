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

        # Get user query
        query = message.text.split(' ', 1)[1].strip()
        if not query:  # Check if query is empty
            await message.reply_text("Please provide a valid query.")
            return

        # Debugging: Show the user query
        print("User Query:", query)

        # Make API request
        try:
            response = requests.post(f"https://chatwithai.codesearch.workers.dev/?chat={query}", timeout=10)
            
            # Debugging: Show response status code and text
            print("Status Code:", response.status_code)
            print("Response Text:", response.text)

            # Check if response is valid
            if response.status_code == 200:
                try:
                    response_data = response.json()  # Parse JSON response
                    response_text = response_data.get("response", "No valid response from API.")
                except ValueError as e:
                    print("JSON Parsing Error:", str(e))
                    response_text = "API returned invalid JSON format."
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                response_text = f"Error: {response.status_code} - {response.text}"

        except requests.exceptions.RequestException as e:
            print("Request Exception:", str(e))
            response_text = f"Request failed: {str(e)}"

        # Debugging: Final response text to send back
        print("Final Response Text:", response_text)

        # Convert response text to speech
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                tts = gTTS(response_text, lang="en")  # Default language set to English
                tts.save(temp_file.name)
                await app.send_voice(chat_id=message.chat.id, voice=temp_file.name)
        finally:
            os.remove(temp_file.name)

    except Exception as e:
        print("Unexpected Error:", str(e))
        await message.reply_text(f"An unexpected error occurred: {str(e)}")
