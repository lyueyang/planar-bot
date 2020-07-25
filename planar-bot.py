from datetime import datetime, timezone
import os

import requests

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

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


def utc_to_local(ts: float) -> datetime:
    return datetime.utcfromtimestamp(ts).replace(tzinfo=timezone.utc).astimezone(tz=None)


def get_assignments(update, context):
    user_id: int = update.message.from_user.id
    modules_response = requests.get('https://planar.joels.space/planar/api/v1.0/tele/%s/modules' % user_id)

    keyboard: list = []

    for module in modules_response.json()['subjects']:
        module_name = list(module.values())[0]
        keyboard.append([InlineKeyboardButton(module_name, callback_data=module_name), ])

    update.message.reply_text('Please choose which module to check for: ', reply_markup=InlineKeyboardMarkup(keyboard))


def module_button(update, context):
    query = update.callback_query
    query.answer()

    output: str

    user_id: int = update.callback_query.from_user.id
    mod: str = query.data
    url: str = 'https://planar.joels.space/planar/api/v1.0/tele/%s/assignments/%s' % (user_id, mod)

    response = requests.get(url)
    if response.status_code == 200:
        json_response: dict = response.json()
        output = '<b>You have %s assignments for %s:\n\n</b>' % (len(json_response), mod)

        index: int = 1
        for value in json_response.values():
            text_list = list(value['content'].values())
            output += '%s. %s' % (str(index), text_list[0])
            if value['date'] is not None:
                output += '  (Due on: %s)' % utc_to_local(value['date']).date()

            output += '\n'
            index += 1

    else:
        output = 'Sorry, I\'m having some trouble fetching your assignments'

    update.effective_message.reply_html(output)


def main():
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start",
                                  begin,
                                  pass_args=True))

    # Make sure the deep-linking handlers occur *before* the normal /start handler.
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("getassignments", get_assignments, pass_args=True))
    updater.dispatcher.add_handler(CallbackQueryHandler(module_button))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
