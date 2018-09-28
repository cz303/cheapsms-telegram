from telebot import types
from cheapsms import services
import os
token = 'telegram bot token'
is_deploy_version = bool(os.environ.get('PORT'))
server_url = 'https://your_app.herokuapp.com/'

welcome = 'Неоффициальный бот для сервиса CheapSMS. Большинство важных функций сайта перенесено в этот удобный и простой интерфейс в Telegram. Разработчик бота: @truecrinny.'
nums = 'Выберите нужный вам сервис и нажмите на него, чтобы получить информацию и приобрести его.'
login = 'Вы не вошли в свой аккаунт CheapSMS или ваш токен является невалидным. Укажите верный токен в настройках, это нужно для покупки номера, проверки баланса и других важных функций.'
invalid_token = 'Ваш токен API является невалидным. Пожалуйста перейдите в настройки и установите токен.'
token_set = 'Токен API был успешно установлен. Вы всегда можете изменить его в настройках.'
invalid_token_set = 'Введённый токен API является невалидным. Проверьте правильность написания и попробуйте ещё раз.'
no_token_set = 'В этом разделе вы можете изменить/задать свой токен API. Вы не задали токен.'
enter_token = 'Введите ваш токен API. Его можно найти здесь: https://cheapsms.ru/my/api.'
not_enough_money = 'У вас недостаточно денег на счету для покупки'
no_numbers = 'Номера для данного сервиса закончились. Пополнение номеров происходит каждый день в 9:00, 15:00, 21:00.'
operation_canceled = 'Операция успешно отменена, деньги были возвращены на ваш счёт'
code_message = 'Покупка номера для {service}\nВыданный вам номер: <pre>{number}</pre>\nКод: <pre>{code}</pre>'
waiting_code = 'ожидание...'
buyed_message = 'Покупка номера для {service}\nВаш баланс после покупки: {balance}\nВыданный вам номер: <pre>{number}</pre>'
service_data = 'Номера для активации: {service}\nКоличество доступных: {number}\nЦена за 1 штуку: {price}'
balance_message = 'Баланс на вашем аккаунте: {balance} руб.'
settings_token = 'В этом разделе вы можете изменить/задать свой токен API. Текущий токен: <pre>{token}</pre>'
operation_not_found = 'Операция #<pre>{id}</pre> не найдена. Попробуйте завершить её на сайте: https://cheapsms.ru/my/activates'
operation_end = 'Операция #<pre>{id}</pre> была успешно завершена.'
mailing_end = 'Рассылка завершена. Сообщение было отправлено {users} пользователям бота.'
mailing_start = 'Началось выполнение рассылки. Когда она будет законечна, бот отправит её результаты.'

main_menu_buttons = ['☎️ Номера', '💰 Баланс', '⚙️ Настройки']
back_button = '◀️ Назад'
settings_menu_buttons = ['✏️ Изменить', back_button]

buy_activation = 'Купить'
cancel_activation = 'Отмена'
invalid_code = 'Код не подошёл'
number_ready = 'Готов'
end_operation = 'Завершить'

main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
numbers_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
settings_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
balance_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
services_buttons = list()
serv = dict()
clients = dict()
num = dict()

main_menu.add(*main_menu_buttons)
settings_menu.add(*settings_menu_buttons)

for name in list(services.values()):
    services_buttons.append(types.KeyboardButton(name))
services_buttons.append(types.KeyboardButton(back_button))
numbers_menu.add(*services_buttons)


def make_inline_buy_button(service):
    buy_keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text=buy_activation, callback_data=service)
    buy_keyboard.add(button)
    return buy_keyboard


def make_inline_tools_buttons(operation_id):
    tools_keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text=cancel_activation, callback_data='-1_status_' + operation_id)
    button2 = types.InlineKeyboardButton(text=number_ready, callback_data='1_status_' + operation_id)
    tools_keyboard.add(button, button2)
    return tools_keyboard


def make_inline_last_button(operation_id):
    upd_keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text=invalid_code, callback_data='3_status_' + operation_id)
    button2 = types.InlineKeyboardButton(text=end_operation, callback_data='6_status_' + operation_id)
    upd_keyboard.add(button, button2)
    return upd_keyboard
