import datetime
import pandas as pd
import os
import TeleGPT
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

import configparser

curr_dir = os.getcwd()
config = configparser.ConfigParser()
config.read(os.path.join(curr_dir, "telethon.config"))
print(curr_dir)

api_id = config["telethon_credentials"]["api_id"] 
api_hash = config["telethon_credentials"]["api_hash"]
phone = config['telethon_credentials']['phone']
username = config['telethon_credentials']['username']

chats = [] # list of chats to scrape

# Create the client and connect
client = TelegramClient(username, api_id, api_hash)
async def main(phone):
    await client.start()
    print("Client Created")
    # Ensure you're authorized
    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    me = await client.get_me()

    df = pd.DataFrame()
    chats.append(input('Enter channel id: '))
    for chat in chats:
    # Now you are logged in, proceed with scraping
        async for message in client.iter_messages(chat, offset_date=datetime.date.today() - datetime.timedelta(days=6), reverse=True): # right now it's set to get chat history from 6 days ago to current date
            data = { "text" : message.text }
            temp_df = pd.DataFrame(data, index=[0])
            df = pd.concat([temp_df, df.loc[:]]).reset_index(drop=True)
        print("DF Created!")
    try:
        # print(df)
        print(TeleGPT.TeleGPT(df))
    except Exception as e:
        print(f"An error occurred: {e}")
    
with client:
    client.loop.run_until_complete(main(phone))