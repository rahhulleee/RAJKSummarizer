import datetime
import pandas as pd
import os
import TeleGPT
import configparser

from telethon.errors import SessionPasswordNeededError
from telethon import TelegramClient
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes

curr_dir = os.getcwd()
config = configparser.ConfigParser()
config.read(os.path.join(curr_dir, "telethon.config"))
print(curr_dir)

api_id = config["telethon_credentials"]["api_id"]
api_hash = config["telethon_credentials"]["api_hash"]
username = config['telethon_credentials']['username']

chats = [] # list of chats to scrape

# Create the client and connect
client = TelegramClient(username, api_id, api_hash)


# Telegram bot
TOKEN: Final = '6738604120:AAH5F4XeRj8tG2zyoQZHnbp_ZmqmupCXkS8'
BOT_USERNAME: Final = '@TLGRM_GPTbot'
ENTER_PHONE, ENTER_CODE, ENTER_CHANNEL = range(3)
telethon_state = {'phone': None, 'code': None, 'channel': None}
# commands


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to TELGRM_GPT!\n"
                                    "I can summarize chats from your channels!\n"
                                    "Please enter your phone number registered with telegram to start"
                                    "e.g. +6512345678")
    return ENTER_PHONE


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I can summarize your conversations from channels!")


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a custom command")


# handle responses


def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'hello' in processed:
        return 'Hey!'

    if 'ur mother' in processed:
        return 'no ur mother'

    return 'what?'


async def enter_phone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telethon_state['phone'] = update.message.text
    if not client.is_connected():
        await client.connect()
    try:
        if not await client.is_user_authorized():
            await client.send_code_request(telethon_state['phone'])
            await update.message.reply_text("Please enter the code sent to you")
            return ENTER_CODE
        else:
            await update.message.reply_text("Please enter a channel")
            return ENTER_CHANNEL
    except Exception as e:
        await update.message.reply_text(f"{e}")
        return ConversationHandler.END


async def enter_code_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telethon_state['code'] = update.message.text
    try:
        await client.sign_in(telethon_state['phone'], telethon_state['code'])
        await update.message.reply_text("Please enter the channel id")
        await update.message.reply_text("Loading response, please wait...")
        return ENTER_CHANNEL
    except SessionPasswordNeededError:
        await update.message.reply_text("Please enter your password or disable 2FA")
        await client.sign_in(password=update.message.text)
    except Exception as e:
        await update.message.reply_text(f"{e}")

    return ConversationHandler.END


async def enter_channel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telethon_state['channel'] = update.message.text
    df = pd.DataFrame()

    # Now you are logged in, proceed with scraping
    async for message in client.iter_messages(telethon_state['channel'], offset_date=datetime.date.today() - datetime.timedelta(days=6),
                                              reverse=True):
        # right now it's set to get chat history from 6 days ago to current date
        data = {"text": message.text}
        temp_df = pd.DataFrame(data, index=[0])
        df = pd.concat([temp_df, df.loc[:]]).reset_index(drop=True)
    print("DF Created!")
    try:
        # print(df)
        await update.message.reply_text(TeleGPT.TeleGPT(df))
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")

    return ConversationHandler.END


if __name__ == '__main__':
    print('starting bot')
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],
        states={
            ENTER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_phone_handler)],
            ENTER_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_code_handler)],
            ENTER_CHANNEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_channel_handler)]
        },
        fallbacks=[]
    )
    app.add_handler(conv_handler)
    print('polling')
    app.run_polling(allowed_updates=Update.ALL_TYPES)

