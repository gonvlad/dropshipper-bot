import os
import telebot
import logging

from telebot import types
from flask import Flask, request
from time import sleep
from requests import HTTPError
import threading

from text_templates import * 
from tags_handler import handle_tag_action

from CustomPyVinted.vinted import Vinted

TIME_BETWEEN_REQUESTS = 60
TIME_FOR_RESET_APP = 60

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
APP_URL = os.environ['HEROKU_APP_URL'] + BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)
logger = telebot.logger
logger.setLevel(logging.DEBUG)
vinted = Vinted("pl")
main_keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)

tracked_tags = []
tracked_tag_item_IDs = {}


def init_main_keyboard():
    global main_keyboard
    tags_list = types.KeyboardButton(TAGS_LIST_BTN)
    main_keyboard.row(tags_list)
    
    
@bot.message_handler(commands=['start'])
def start(message):    
    username = message.chat.username
    bot.send_message(message.chat.id, WELCOME_MESSAGE.format(username=username), reply_markup=main_keyboard)


@bot.message_handler(content_types=['text'])
def handle_main_keyboard(message):
    chat_id = message.chat.id
    if message.text == TAGS_LIST_BTN:
        if len(tracked_tags) > 0:
            text = TAG_LIST_CAPTION + "\n\n"
            for tag in tracked_tags:
                text += tag + "\n"
        else:
            text = EMPTY_TAG_LIST_СAPTION
        bot.send_message(chat_id, text)
    elif message.text.startswith(ADD_ACTION_SIGN) or message.text.startswith(REMOVE_ACTION_SIGN):
        action = message.text[0]
        tag = message.text[1:].strip()
        result = handle_tag_action(action, tag, tracked_tags)
        if result == TAG_ADDED:
            tracked_tags.append(tag)
        elif result == TAG_REMOVED:
            tracked_tags.remove(tag)
            del tracked_tag_item_IDs[tag]
        bot.send_message(chat_id, result)
        

@server.route(f"/{BOT_TOKEN}", methods=["POST"])
def get_message():
   json_string = request.get_data().decode("utf-8")
   update = telebot.types.Update.de_json(json_string)
   bot.process_new_updates([update])
   return "!", 200


@server.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    return '!', 200


def run_server():
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


if __name__ == "__main__":
    init_main_keyboard()
    
    print("[ >> ] Starting server...")
    t = threading.Thread(target=run_server, args=())
    t.start()

    print("[ >> ] Starting main loop...")
    while True:
        try:
            for tag in tracked_tags:
                tag_ = tag.replace(" ", "%20")

                # Poland config
                items = vinted.items.search(f"https://www.vinted.pl/ubrania?search_text={tag_}&order=newest_first")
                
                # France config
                #items = vinted.items.search(f"https://www.vinted.fr/vetements?search_text={tag_}&order=newest_first")

                if tag not in tracked_tag_item_IDs.keys():
                    tracked_tag_item_IDs[tag] = [] 
                    for item in items:
                        tracked_tag_item_IDs[tag].append(item.id)
                else:
                    for item in items:
                        if item.id not in tracked_tag_item_IDs[tag]:
                            tracked_tag_item_IDs[tag].append(item.id)
                            
                            url = item.url
                            photo = item.photo
                            caption = CAPTION_TEMPLATE.format(title=item.title, 
                                                            brand=item.brand_title, 
                                                            price=item.price, 
                                                            currency=item.currency)
                            markup = types.InlineKeyboardMarkup()
                            link_btn = types.InlineKeyboardButton(VIEW_ITEM_BTN, url=url, callback_data=VIEW_ITEM_BTN_DATA)
                            markup.row(link_btn)
                            bot.send_photo(CHAT_ID, photo=photo, caption=caption, reply_markup=markup)
                        else:
                            break    
            sleep(TIME_BETWEEN_REQUESTS)
        except HTTPError as e:
            status_code = e.response.status_code
            print("[ >> ] HTTP Error occured | Status code " + str(status_code))
            sleep(TIME_FOR_RESET_APP)
        except KeyboardInterrupt:
            print("[ >> ] Application stopped")
            t.join()
            exit(0)
        except ConnectionResetError:
            print("[ >> ] Restarting application in " + str(TIME_FOR_RESET_APP) + " seconds")
            sleep(TIME_FOR_RESET_APP)
            