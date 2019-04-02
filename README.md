# Установка
### Локальная

- Установить Python 3.6+ а также Redis
- В файле config.py изменить переменную token, owner_id на ваш ID Telegram, и по желанию текстовые переменные, содержащие шаблоны сообщений от бота
- Запустить локально БД Redis на портe 6379
- Установить необходимые библиотеки из файла requirements.txt
- Запустить бота используя команду `python main.py`.
- Нажать на репозитории Star :)

### На Heroku

- Создать приложение на Heroku
- Выбрать Python buildpack в настройках приложения
- В файле config.py изменить переменную token, server_url, owner_id на ваш ID Telegram и по желанию текстовые переменные, содержащие шаблоны сообщений от бота
- Добавить во вкладке ресурсов аддон Heroku Redis
- Задеплоить скрипт используя приватный репозиторий GitHub, например
- Включить во вкладке ресурсов все возможные worker и ждать запуска бота.
- Нажать на репозитории Star :)
