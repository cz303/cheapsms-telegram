from telebot import TeleBot
import telebot
from cheapsms import CheapSMS, services, BadKeyError, NoNumbersError, NoActivationError, NoBalanceError
from config import *
import redis
import requests
import lxml.html as html
import os
from threading import Thread
from flask import Flask, request
server = Flask(__name__)
bot = TeleBot(token, threaded=True)


class CodeThread(Thread):
    def __init__(self, token, operation_id, chat_id, message_id):
        Thread.__init__(self)
        self.token = token
        self.operation_id = operation_id
        self.chat_id = chat_id
        self.message_id = message_id

    def run(self):
        while True:
            status = clients[self.chat_id].get_status(self.operation_id).code
            if status is not None:
                bot.edit_message_text(chat_id=self.chat_id, message_id=self.message_id, text=code_message.format(service=serv[self.chat_id], number=num[self.chat_id].number, code=status), reply_markup=make_inline_last_button(self.operation_id), parse_mode='HTML')


class ParserThread(Thread):
    def __init__(self, message):
        Thread.__init__(self)
        self.message = message

    def run(self):
        key = list(services.keys())[list(services.values()).index(self.message.text)]
        text = requests.get('https://cheapsms.ru/').text
        content = html.document_fromstring(text)
        response = content.xpath("//li[@data-id='{}']/label/div/span/text()".format(key))
        answer = service_data.format(service=self.message.text, number=response[1], price=response[0])
        if int(response[1].replace(' шт', '')) < 1:
            bot.send_message(self.message.chat.id, answer, parse_mode='HTML')
        else:
            keyboard = make_inline_buy_button(key)
            bot.send_message(self.message.chat.id, answer, reply_markup=keyboard, parse_mode='HTML')


class BalanceThread(Thread):
    def __init__(self, token, message):
        Thread.__init__(self)  
        self.token = token
        self.message = message

    def run(self):
        if check_token(self.token):
            token = self.token.decode('utf-8')
            new_client = CheapSMS(api_key=token)
            balance = new_client.get_balance()
            bot.send_message(self.message.chat.id, balance_message.format(balance=balance), reply_markup=main_menu, parse_mode='HTML')
        else:
            bot.send_message(self.message.chat.id, invalid_token, reply_markup=main_menu, parse_mode='HTML')


def create_code_thread(token, operation_id, chat_id, message_id):
    thread = CodeThread(token, operation_id, chat_id, message_id)
    thread.start()


def create_parser_thread(message):
    thread = ParserThread(message)
    thread.start()


def create_balance_thread(token, message):
    thread = BalanceThread(token, message)
    thread.start()


def check_token(token):
    try:
        CheapSMS(api_key=token).get_balance()
    except BadKeyError:
        return False
    return True


def save_api_key(message):
    if message.text == back_button:
        bot.send_message(message.chat.id, welcome, reply_markup=main_menu, parse_mode='HTML')
    else:
        if check_token(message.text):
            r.set(message.from_user.id, message.text)
            bot.send_message(message.chat.id, token_set, reply_markup=settings_menu, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, invalid_token_set, reply_markup=settings_menu, parse_mode='HTML')


@server.route('/' + token, methods=['POST'])
def get_message():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=server_url + token)
    return "!", 200


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, welcome, reply_markup=main_menu, parse_mode='HTML')


@bot.message_handler(commands=['send'])
def send_mailing(message):
    if message.from_user.id == owner_id:
        sent_message = bot.send_message(message.chat.id, mailing_start, parse_mode='HTML')
        text_to_send = message.text.replace('/send ', '')
        times_send = 0
        for user_id in r.scan_iter():
            try:
                bot.send_message(user_id.decode('utf-8'), text_to_send, parse_mode='HTML')
                times_send += 1
            except Exception:
                pass
        bot.edit_message_text(chat_id=message.chat.id, message_id=sent_message.message_id, text=mailing_end.format(users=str(times_send)), parse_mode='HTML')


@bot.message_handler(func=lambda m: m.text == back_button)
def send_welcome(message):
    bot.send_message(message.chat.id, welcome, reply_markup=main_menu, parse_mode='HTML')


@bot.message_handler(func=lambda m: m.text == main_menu_buttons[0])
def send_numbers(message):
    bot.send_message(message.chat.id, nums, reply_markup=numbers_menu, parse_mode='HTML')


@bot.message_handler(func=lambda m: m.text == main_menu_buttons[2])
def send_settings(message):
    if r.get(message.from_user.id) is not None:
        bot.send_message(message.chat.id, settings_token.format(token=r.get(message.from_user.id).decode('utf-8')), reply_markup=settings_menu, parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, no_token_set, reply_markup=settings_menu, parse_mode='HTML')


@bot.message_handler(func=lambda m: m.text == settings_menu_buttons[0])
def send_change(message):
    bot.register_next_step_handler_by_chat_id(message.chat.id, save_api_key)
    bot.send_message(message.chat.id, enter_token, reply_markup=settings_menu, parse_mode='HTML')


@bot.message_handler(func=lambda m: m.text == main_menu_buttons[1])
def send_balance(message):
    create_balance_thread(r.get(message.chat.id), message)


@bot.message_handler(func=lambda m: m.text in list(services.values()))
def send_service_info(message):
    create_parser_thread(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    token = r.get(call.message.chat.id)
    if check_token(token):
        clients[call.message.chat.id] = CheapSMS(api_key=token, ref='cheapbott')
    else:
        bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text=login)

    if call.message:
        if call.data in list(services.keys()):
            if r.get(call.message.chat.id) is None:
                bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text=login)
            else:
                try:
                    num[call.message.chat.id] = clients[call.message.chat.id].get_number(call.data)
                    balance = clients[call.message.chat.id].get_balance()
                    serv[call.message.chat.id] = services[call.data]
                    markup = make_inline_tools_buttons(num[call.message.chat.id].id)
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=buyed_message.format(service=serv[call.message.chat.id], balance=balance, number=num[call.message.chat.id].number), reply_markup=markup, parse_mode='HTML')

                except NoNumbersError:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=no_numbers, parse_mode='HTML')

                except NoBalanceError:
                    bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text=not_enough_money)

        elif len(call.data.split('_status_')) == 2:
            info = call.data.split('_status_')
            status = info[0]
            operation_id = info[1]
            try:
                response = clients[call.message.chat.id].set_status(status, operation_id)
                if response == 'ACCESS_CANCEL':
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=operation_canceled, parse_mode='HTML')

                elif response == 'ACCESS_READY' or response == 'ACCESS_RETRY_GET':
                    if num[call.message.chat.id] is not None:
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=code_message.format(service=serv[call.message.chat.id], number=num[call.message.chat.id].number, code=waiting_code), parse_mode='HTML')
                        create_code_thread(clients[call.message.chat.id], chat_id=call.message.chat.id, message_id=call.message.message_id, operation_id=num[call.message.chat.id].id)
                    else:
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=operation_not_found.format(operation_id), parse_mode='HTML')

                elif response == 'ACCESS_ACTIVATION':
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=operation_end.format(id=operation_id), parse_mode='HTML')

            except NoActivationError:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=operation_not_found.format(operation_id), parse_mode='HTML')


if __name__ == '__main__':
    if is_deploy_version:
        r = redis.from_url(os.environ.get("REDIS_URL"))
        bot.remove_webhook()
        bot.set_webhook(url=server_url + token)
        server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
    else:
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        bot.polling(none_stop=True)
