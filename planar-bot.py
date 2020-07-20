import datetime
import os

import requests
import telegram
from telegram.ext import Updater, CommandHandler

TOKEN = os.environ.get('TOKEN')


def start(update, context):
    print('')

def begin(update, context):
    bot = context.bot
    payload = context.args
    if len(payload) > 0:
        text = "Congratulations! You've linked your account!"

        # log successful links
        user = update.message.from_user.username
        text2 = str(user) + " " + str(datetime.datetime.now()) + " " + str(payload)
        print(text2, file=open("botFiles/log.txt", "a"))
    else:
        text = "Welcome to planar bot! To start linking your account, please head to the web-app!"

    update.message.reply_text(text)


def main():
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start",
                                  begin,
                                  pass_args=True))

    # Make sure the deep-linking handlers occur *before* the normal /start handler.
    dp.add_handler(CommandHandler("start", start))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
