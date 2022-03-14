import logging
from telegram import BotCommand, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import re
import requests
import os

from src.shopee.sqlite.shopee_products import create_table, insert_product, get_products, update_product, delete_product


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# set my commands
commands = [BotCommand('setalert', 'add alert product in shopee'),
            BotCommand('getid', 'get member id'),
            BotCommand('cancel', 'cancel command bot'),
            BotCommand('help', 'help bot')]


# stages
SET_ALERT = range(1)
# callback data
ITEMID, SHOPID = range(2)
# end
END = ConversationHandler.END


# start command
def start(update: Update, context: CallbackContext):
    return context.bot.send_message(
        chat_id=update.effective_chat.id, text="<b>I'm a bot, please talk to me!</b>", parse_mode='HTML')


# set alert command
def set_alert(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='<b>You choose to add a product shopee,please paste link. To abort command, simply type /cancel</b>', parse_mode='HTML')
    return SET_ALERT


def set_alert_input(update: Update, context: CallbackContext):
    paste_link = update.message.text
    regex_desktop = r'(\-i).(\d+).(\d+)'
    regex_mobile = r'(https:\/\/shopee.co.th\/product)\/(\d+).(\d+)'
    search_shopee_desktop = re.search('https://shopee.co.th/', paste_link)
    print(search_shopee_desktop)
    replace_link_desktop = re.search(regex_desktop, paste_link)
    print(replace_link_desktop)
    replace_link_mobile = re.search(regex_mobile, paste_link)
    print(replace_link_mobile)
    if((search_shopee_desktop is None or replace_link_desktop is None) and replace_link_mobile is None):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'<b>Invalid link</b>', parse_mode='HTML')
        return SET_ALERT
    else:
        replace_shopid = ''
        replace_itemid = ''
        if(replace_link_desktop is not None):
            replace_shopid = replace_link_desktop.group(2)
            replace_itemid = replace_link_desktop.group(3)
        if(replace_link_mobile is not None):
            replace_shopid = replace_link_mobile.group(2)
            replace_itemid = replace_link_mobile.group(3)
        user_data = context.user_data
        user_data[SHOPID] = replace_shopid
        user_data[ITEMID] = replace_itemid
        ISHOPID = context.user_data.get(SHOPID)
        IITEMID = context.user_data.get(ITEMID)
        print(ISHOPID, ITEMID)
        product = {
            'userid': update.effective_chat.id,
            'itemid': IITEMID,
            'shopid': ISHOPID
        }
        if(insert_product(product) == None):
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f'<b>You already have this product alert or Cannot set alert try again</b>', parse_mode='HTML')
            return SET_ALERT
        else:
            # insert_product(product)
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f'<b>Set alert finish</b>', parse_mode='HTML')
    return END


# get member id command
def get_member_id(update: Update, context: CallbackContext):
    return context.bot.send_message(chat_id=update.effective_chat.id, text=f'<b>Member id: {update._effective_user.id} </b>', parse_mode='HTML')


# cancel command
def cancel(update: Update, context: CallbackContext):
    print('cancel')
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='<b>Cancel conversation command</b>', parse_mode='HTML')

    return END


# help command
def help(update: Update, context: CallbackContext):
    return context.bot.send_message(chat_id=update.effective_chat.id, text="<b>Commands\n\n/setalert - add alert product in shopee\n/getid - get member id\n/cancel - cancel command bot</b>", parse_mode='HTML')

# callback command unknown


def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="<b>Sorry, I didn't understand that command</b>", parse_mode='HTML')
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="<b>Commands\n\n/setalert - add alert product in shopee\n/getid - get member id\n/cancel - cancel command bot</b>", parse_mode='HTML')


def alert(context: CallbackContext):
    products = get_products()
    for p in products:
        id_db = p['id']
        userid_db = p['userid']
        shopid_db = p['shopid']
        itemid_db = p['itemid']
        count_db = p['count']
        url_api = f'https://shopee.co.th/api/v4/item/get?itemid={itemid_db}&shopid={shopid_db}'
        res = requests.get(url_api).json()
        data = res['data']
        itemid = data['itemid']
        shopid = data['shopid']
        item_status = data['item_status']
        stock = data['stock']
        image = data['image']
        url_image = f'https://cf.shopee.co.th/file/{image}'
        slug = f'https://shopee.co.th/product/{shopid}/{itemid}'
        if item_status == 'normal':
            u_product = {
                'id': id_db,
                'userid': userid_db,
                'itemid': itemid_db,
                'shopid': shopid_db,
                'count': count_db - 1
            }

            update_product(u_product)

            if(count_db == 0):
                delete_product(id_db)
                print('deleted')
            elif(count_db > 0):
                print(f'count {count_db}')
            context.bot.send_photo(chat_id=userid_db, photo=url_image,
                                   caption=f"<b>status: instock\nstock: {stock}\n{slug}\n</b>", parse_mode='HTML')
        else:
            print('out stock')


def main():
    create_table()
    updater = Updater(os.environ['BOT_TOKEN'])
    job = updater.job_queue
    dispatcher = updater.dispatcher
    dispatcher.bot.set_my_commands(commands)

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    set_alert_handler = CommandHandler('setalert', set_alert)
    cancel_handler = CommandHandler('cancel', cancel)

    set_alert_conv_handler = ConversationHandler(
        entry_points=[set_alert_handler],
        states={SET_ALERT: [MessageHandler(
            Filters.text & (~Filters.command), set_alert_input)]},
        fallbacks=[cancel_handler])
    dispatcher.add_handler(set_alert_conv_handler)

    get_member_id_handler = CommandHandler('getid', get_member_id)
    dispatcher.add_handler(get_member_id_handler)

    help_handler = CommandHandler('help', help)
    dispatcher.add_handler(help_handler)

    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    job.run_repeating(alert, interval=300, first=10)

    updater.start_polling()
    updater.idle()
    updater.stop()


if __name__ == "__main__":
    main()
