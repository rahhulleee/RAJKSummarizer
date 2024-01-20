from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes


TOKEN: Final = '6738604120:AAH5F4XeRj8tG2zyoQZHnbp_ZmqmupCXkS8'
BOT_USERNAME: Final = '@TLGRM_GPTbot'

ENTER_PHONE, ENTER_CODE = range(2)

# commands


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to TELGRM_GPT!\n"
                                    "I can summarize chats from your channels!\n"
                                    "Please enter your phone number registered with telegram to start")
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
    context.user_data["phone_number"] = update.message.text
    await update.message.reply_text("Please enter the code sent to you")
    return ENTER_CODE


async def enter_code_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["code"] = update.message.text
    return ConversationHandler.END

if __name__ == '__main__':
    print('starting bot')
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],
        states={
            ENTER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_phone_handler)],
            ENTER_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_code_handler)]
        },
        fallbacks=[]
    )
    app.add_handler(conv_handler)
    print('polling')
    app.run_polling(allowed_updates=Update.ALL_TYPES)

