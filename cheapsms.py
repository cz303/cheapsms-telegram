import requests
import json


class BadKeyError(Exception):
    def __init__(self):
        message = 'Неверный API-ключ'
        super().__init__(message)


class SQLError(Exception):
    def __init__(self):
        message = 'Ошибка SQL-сервера'
        super().__init__(message)


class NoNumbersError(Exception):
    def __init__(self):
        message = 'Нет номеров'
        super().__init__(message)


class NoBalanceError(Exception):
    def __init__(self):
        message = 'Закончился баланс'
        super().__init__(message)


class NoActivationError(Exception):
    def __init__(self):
        message = 'ID активации не существует'
        super().__init__(message)


class BadServiceError(Exception):
    def __init__(self):
        message = 'Некоректное наименование сервиса'
        super().__init__(message)


class BadStatusError(Exception):
    def __init__(self):
        message = 'Некоректный статус'
        super().__init__(message)


class BadActionError(Exception):
    def __init__(self):
        message = 'Некоректное действие'
        super().__init__(message)


errors = {
    'BAD_KEY': BadKeyError,
    'ERROR_SQL': SQLError,
    'NO_NUMBERS': NoNumbersError,
    'NO_BALANCE': NoBalanceError,
    'NO_ACTIVATION': NoActivationError,
    'BAD_SERVICE': BadServiceError,
    'BAD_STATUS': BadStatusError,
    'BAD_ACTION': BadActionError,
}


def send_api_request(self, params, jsons):
    response = requests.get(self.api_domain, params=params)
    if response.text in errors:
        raise errors[response.text]

    if not jsons:
        return response.text
    return json.loads(response.text)


class CheapSMS:
    def __init__(self, api_key, ref=None):
        self.api_key = api_key
        self.api_domain = 'http://cheapsms.ru/stubs/handler_api.php'
        self.ref = ref

    def set_status(self, status, id):
        data = {'action': 'setStatus', 'api_key': self.api_key, 'id': id, 'status': status}
        response = send_api_request(self, data, jsons=False)
        return response

    def get_numbers_status(self):
        data = {'action': 'getNumbersStatus', 'api_key': self.api_key}
        response = send_api_request(self, data, jsons=True)
        return response

    def get_balance(self):
        data = {'action': 'getBalance', 'api_key': self.api_key}
        response = send_api_request(self, data, jsons=False)
        return response.replace('ACCESS_BALANCE:', '')

    def get_number(self, service):
        data = {'action': 'getNumber', 'api_key': self.api_key, 'service': service}
        if self.ref is not None:
            data['ref'] = self.ref
        response = send_api_request(self, data, jsons=False)
        response = response.split(':')
        return Operation(self.api_key, response[1], service, response[2])

    def get_status(self, id):
        data = {'action': 'getStatus', 'api_key': self.api_key, 'id': id}
        response = send_api_request(self, data, jsons=False)
        if len(response.split(':')) > 1:
            code = response.split(':')[1]
            status = response.split(':')[0]
        else:
            code = None
            status = response
        return Status(status, code)


class Status:
    def __init__(self, status, code):
        self.status = status
        self.code = code


class Operation:
    def __init__(self, api_key, id, service, number):
        self.api_domain = 'http://cheapsms.ru/stubs/handler_api.php'
        self.api_key = api_key
        self.id = id
        self.service = service
        self.number = number

    def check_code(self):
            status = self.get_status()
            if status.code:
                return status.code
            else:
                return None

    def set_status(self, status):
        data = {'action': 'setStatus', 'api_key': self.api_key, 'id': self.id, 'status': status}
        response = send_api_request(self, data, jsons=False)
        return response

    def get_status(self):
        data = {'action': 'getStatus', 'api_key': self.api_key, 'id': self.id}
        response = send_api_request(self, data, jsons=False)
        if len(response.split(':')) > 1:
            code = response.split(':')[1]
            status = response.split(':')[0]
        else:
            code = None
            status = response
        return Status(status, code)
