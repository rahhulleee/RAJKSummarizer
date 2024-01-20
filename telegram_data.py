import pandas as pd
import os
import TeleGPT
from telethon.sync import TelegramClient
from telethon import TelegramClient
import datetime

import configparser

curr_dir = os.getcwd()
config = configparser.ConfigParser()
config.read(os.path.join(curr_dir, "telethon.config"))

api_id = config["telethon_credentials"]["api_id"] 
api_hash = config["telethon_credentials"]["api_hash"]
phone_number = config['telethon_credentials']['phone']
username = config['telethon_credentials']['username']

chats = ['nuscomputingclub'] # list of chats to scrape

# Path to the session file
session_file = f'/Users/kaichen/Desktop/Personal Development/Events/Hack & Roll/TLGRM_GPT/{username}.session'

# Create the Telegram client
print("Creating the Telegram client...")
client = TelegramClient(session_file, api_id, api_hash)
print("Telegram client created!")

# client = TelegramClient(username, api_id, api_hash)
async def main():
    # Connect to the Telegram server
    print("Connecting to the Telegram servers...")
    await client.connect()
    print("Connected to the Telegram servers!")

    # Check if the user is already authorized
    if not await client.is_user_authorized():
        print("User is not authorized. Sending code request...")
        
        # Send code request to the phone number
        await client.send_code_request(phone_number)

        # Prompt the user to enter the received code
        code = input('Please enter the code you received: ')

        try:
            # Sign in with the entered code
            await client.sign_in(phone_number, code)
            print("Signed in successfully!")

        except Exception as e:
            # Handle possible exceptions (e.g., Two-Step Verification password required)
            print(f"An error occurred: {e}")

    else:
        print("User is already authorized.")

    df = pd.DataFrame() # dataframe to store scraped data
    for chat in chats:
    # Now you are logged in, proceed with scraping
        async for message in client.iter_messages(chat, offset_date=datetime.date.today() - datetime.timedelta(days=6), reverse=True): # right now it's set to get chat history from 6 days ago to current date
            data = { "text" : message.text }
            temp_df = pd.DataFrame(data, index=[0])
            df = pd.concat([temp_df, df.loc[:]]).reset_index(drop=True)
        print("Dataframe Created!")
    try:
        print("Running TeleGPT...")
        question = "Here are the text messages from a telegram channel, summarise the contents in less than 500 words.\n"
        print(TeleGPT.TeleGPT(df,question))
    except Exception as e:
        print(f"An error occurred: {e}")


# Run the main function
print("Starting...")
with client:
    print("Starting the script...")
    client.loop.run_until_complete(main())